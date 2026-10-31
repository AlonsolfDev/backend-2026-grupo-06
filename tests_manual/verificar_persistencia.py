"""
Verificación de persistencia e integridad referencial (punto 5.8).

Uso (desde la raíz del repo):
  python -m tests_manual.verificar_persistencia crear
  python -m tests_manual.verificar_persistencia verificar
  python -m tests_manual.verificar_persistencia integridad

'crear' y 'verificar' deben correrse en procesos separados para probar
que el dato sobrevive al reinicio.
"""
import sys
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app.domain.entities import EstadoReserva, EstadoSala, Sala
from app.infrastructure.database import SessionLocal
from app.infrastructure.models import ReservaModel
from app.infrastructure.repositories.sala_repository import SalaRepository

NOMBRE_PRUEBA = "Sala de prueba persistencia"


def crear() -> None:
    db = SessionLocal()
    try:
        sala = SalaRepository(db).crear(
            Sala(id=0, nombre=NOMBRE_PRUEBA, capacidad=5,
                 ubicacion="Prueba", estado=EstadoSala.DISPONIBLE)
        )
        print(f"OK: sala creada con ID {sala.id}")
    finally:
        db.close()


def verificar() -> None:
    db = SessionLocal()
    try:
        salas = SalaRepository(db).listar()
        if any(s.nombre == NOMBRE_PRUEBA for s in salas):
            print("OK: la sala sobrevivió al reinicio")
        else:
            print("FALLA: la sala no existe en un proceso nuevo")
    finally:
        db.close()


def integridad() -> None:
    db = SessionLocal()
    try:
        db.add(ReservaModel(
            usuario_id=99999, sala_id=99999,
            fecha_inicio=datetime(2026, 11, 5, 9, 0),
            fecha_fin=datetime(2026, 11, 5, 10, 0),
            proposito="prueba de integridad", num_asistentes=1,
            estado=EstadoReserva.PENDIENTE,
        ))
        db.commit()
        print("FALLA: se aceptó una reserva con usuario y sala inexistentes")
    except IntegrityError:
        db.rollback()
        print("OK: la base rechazó la referencia inexistente")
    finally:
        db.close()


if __name__ == "__main__":
    comandos = {"crear": crear, "verificar": verificar, "integridad": integridad}
    if len(sys.argv) != 2 or sys.argv[1] not in comandos:
        print("Uso: python -m tests_manual.verificar_persistencia [crear|verificar|integridad]")
        sys.exit(1)
    comandos[sys.argv[1]]()
