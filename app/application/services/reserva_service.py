"""
Casos de uso de Reserva: lógica de negocio, validaciones y coordinación
con el repositorio.
"""
from dataclasses import replace

from sqlalchemy.orm import Session

from app.domain.entities import Reserva, EstadoReserva
from app.domain.reglas_negocio import (
    validar_fechas_reserva,
    validar_disponibilidad_sala,
)
from app.infrastructure.repositories.reserva_repository import ReservaRepository
from app.infrastructure.repositories.sala_repository import SalaRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.presentation.schemas.dtos import ReservaCreate


def _validar_existencia_relacionada(db: Session, usuario_id: int, sala_id: int) -> None:
    if UsuarioRepository(db).obtener_por_id(usuario_id) is None:
        raise ValueError(f"No existe un usuario con ID {usuario_id}.")
    if SalaRepository(db).obtener_por_id(sala_id) is None:
        raise ValueError(f"No existe una sala con ID {sala_id}.")


def crear_reserva(db: Session, data: ReservaCreate) -> Reserva:
    _validar_existencia_relacionada(db, data.usuario_id, data.sala_id)
    validar_fechas_reserva(data.fecha_inicio, data.fecha_fin)

    repo = ReservaRepository(db)
    validar_disponibilidad_sala(
        data.sala_id, data.fecha_inicio, data.fecha_fin, repo.listar()
    )

    nueva = Reserva(
        id=0,  # el repositorio asigna el ID real
        usuario_id=data.usuario_id,
        sala_id=data.sala_id,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
        proposito=data.proposito,
        num_asistentes=data.num_asistentes,
        estado=EstadoReserva.PENDIENTE,
    )
    return repo.crear(nueva)


def listar_reservas(db: Session) -> list[Reserva]:
    return ReservaRepository(db).listar()


def obtener_reserva(db: Session, reserva_id: int) -> Reserva:
    reserva = ReservaRepository(db).obtener_por_id(reserva_id)
    if reserva is None:
        raise ValueError(f"No existe una reserva con ID {reserva_id}.")
    return reserva


def actualizar_reserva(db: Session, reserva_id: int, data: ReservaCreate) -> Reserva:
    actual = obtener_reserva(db, reserva_id)
    _validar_existencia_relacionada(db, data.usuario_id, data.sala_id)
    validar_fechas_reserva(data.fecha_inicio, data.fecha_fin)

    repo = ReservaRepository(db)
    otras = [r for r in repo.listar() if r.id != reserva_id]
    validar_disponibilidad_sala(data.sala_id, data.fecha_inicio, data.fecha_fin, otras)

    actualizada = replace(
        actual,
        usuario_id=data.usuario_id,
        sala_id=data.sala_id,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
        proposito=data.proposito,
        num_asistentes=data.num_asistentes,
        # el estado se conserva: actualizar no debe reiniciar una reserva confirmada
    )
    return repo.actualizar(actualizada)


def confirmar_reserva(db: Session, reserva_id: int) -> Reserva:
    reserva = obtener_reserva(db, reserva_id)

    repo = ReservaRepository(db)
    otras = [r for r in repo.listar() if r.id != reserva_id]
    validar_disponibilidad_sala(
        reserva.sala_id, reserva.fecha_inicio, reserva.fecha_fin, otras
    )

    confirmada = replace(reserva, estado=EstadoReserva.CONFIRMADA)
    return repo.actualizar(confirmada)


def eliminar_reserva(db: Session, reserva_id: int) -> None:
    obtener_reserva(db, reserva_id)  # lanza error si no existe
    ReservaRepository(db).eliminar(reserva_id)