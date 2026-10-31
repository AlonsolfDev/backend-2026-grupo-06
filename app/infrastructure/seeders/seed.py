from datetime import datetime

from app.domain.entities import (
    EstadoEquipamiento,
    EstadoReserva,
    EstadoSala,
    RolUsuario,
)
from app.infrastructure.database import SessionLocal
from app.infrastructure.models import (
    EquipamientoModel,
    ReservaModel,
    SalaModel,
    UsuarioModel,
)


def _obtener_o_crear(db, modelo, filtro: dict, datos: dict):
    existente = db.query(modelo).filter_by(**filtro).first()
    if existente:
        return existente
    instancia = modelo(**datos)
    db.add(instancia)
    db.flush()
    return instancia


def seed() -> None:
    db = SessionLocal()
    try:
        ana = _obtener_o_crear(
            db, UsuarioModel, {"correo": "ana@uct.cl"},
            {"nombre": "Ana Pérez", "correo": "ana@uct.cl",
             "rol": RolUsuario.DOCENTE, "activo": True},
        )
        luis = _obtener_o_crear(
            db, UsuarioModel, {"correo": "luis@uct.cl"},
            {"nombre": "Luis Soto", "correo": "luis@uct.cl",
             "rol": RolUsuario.ESTUDIANTE, "activo": True},
        )

        sala_a = _obtener_o_crear(
            db, SalaModel, {"nombre": "Sala A101"},
            {"nombre": "Sala A101", "capacidad": 30,
             "ubicacion": "Edificio A, piso 1", "estado": EstadoSala.DISPONIBLE},
        )
        sala_b = _obtener_o_crear(
            db, SalaModel, {"nombre": "Sala B202"},
            {"nombre": "Sala B202", "capacidad": 12,
             "ubicacion": "Edificio B, piso 2", "estado": EstadoSala.DISPONIBLE},
        )

        _obtener_o_crear(
            db, EquipamientoModel, {"nombre": "Proyector", "sala_id": sala_a.id},
            {"nombre": "Proyector", "tipo": "audiovisual",
             "estado": EstadoEquipamiento.DISPONIBLE,
             "descripcion": "Proyector HDMI", "sala_id": sala_a.id},
        )
        _obtener_o_crear(
            db, EquipamientoModel, {"nombre": "Pizarra digital", "sala_id": sala_b.id},
            {"nombre": "Pizarra digital", "tipo": "audiovisual",
             "estado": EstadoEquipamiento.DISPONIBLE,
             "descripcion": "Pizarra táctil", "sala_id": sala_b.id},
        )

        _obtener_o_crear(
            db, ReservaModel,
            {"usuario_id": ana.id, "sala_id": sala_a.id,
             "fecha_inicio": datetime(2026, 11, 2, 9, 0)},
            {"usuario_id": ana.id, "sala_id": sala_a.id,
             "fecha_inicio": datetime(2026, 11, 2, 9, 0),
             "fecha_fin": datetime(2026, 11, 2, 11, 0),
             "proposito": "Clase de Backend", "num_asistentes": 25,
             "estado": EstadoReserva.CONFIRMADA},
        )
        _obtener_o_crear(
            db, ReservaModel,
            {"usuario_id": luis.id, "sala_id": sala_b.id,
             "fecha_inicio": datetime(2026, 11, 3, 14, 0)},
            {"usuario_id": luis.id, "sala_id": sala_b.id,
             "fecha_inicio": datetime(2026, 11, 3, 14, 0),
             "fecha_fin": datetime(2026, 11, 3, 15, 30),
             "proposito": "Estudio grupal", "num_asistentes": 5,
             "estado": EstadoReserva.PENDIENTE},
        )

        db.commit()
        print("Seeders ejecutados correctamente")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()