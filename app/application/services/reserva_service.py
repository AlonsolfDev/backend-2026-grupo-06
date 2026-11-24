"""
Casos de uso de Reserva: lógica de negocio, validaciones y coordinación
con el repositorio.
"""

import math
from dataclasses import replace
from datetime import date

from sqlalchemy.orm import Session

from app.domain.entities import EstadoReserva, Reserva
from app.domain.errores import ConflictoError, RecursoNoEncontrado
from app.domain.reglas_negocio import (
    validar_capacidad_sala,
    validar_disponibilidad_sala,
    validar_equipamiento_disponible,
    validar_fechas_reserva,
    validar_sala_operativa,
)
from app.infrastructure.repositories.equipamiento_repository import EquipamientoRepository
from app.infrastructure.repositories.reserva_repository import ReservaRepository
from app.infrastructure.repositories.sala_repository import SalaRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.presentation.schemas.dtos import ReservaCreate


def _validar_existencia_relacionada(db: Session, usuario_id: int, sala_id: int):
    if UsuarioRepository(db).obtener_por_id(usuario_id) is None:
        raise RecursoNoEncontrado(f"No existe un usuario con ID {usuario_id}.")
    sala = SalaRepository(db).obtener_por_id(sala_id)
    if sala is None:
        raise RecursoNoEncontrado(f"No existe una sala con ID {sala_id}.")
    return sala


def crear_reserva(db: Session, data: ReservaCreate) -> Reserva:
    sala = _validar_existencia_relacionada(db, data.usuario_id, data.sala_id)
    validar_sala_operativa(sala)
    validar_capacidad_sala(sala, data.num_asistentes)
    validar_fechas_reserva(data.fecha_inicio, data.fecha_fin)

    repo = ReservaRepository(db)
    validar_disponibilidad_sala(data.sala_id, data.fecha_inicio, data.fecha_fin, repo.listar())

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


def listar_reservas_paginado(
    db: Session,
    usuario_id: int | None = None,
    sala_id: int | None = None,
    estado: EstadoReserva | None = None,
    fecha: date | None = None,
    ordenar_por: str = "fecha_inicio",
    direccion: str = "asc",
    pagina: int = 1,
    limite: int = 20,
) -> dict:
    # El repositorio filtra, ordena y pagina en la base de datos (en ese orden)
    items, total = ReservaRepository(db).listar_paginado(
        usuario_id, sala_id, estado, fecha, ordenar_por, direccion, pagina, limite
    )
    total_paginas = math.ceil(total / limite) if total > 0 else 0

    return {
        "items": items,
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "total_paginas": total_paginas,
    }


def obtener_reserva(db: Session, reserva_id: int) -> Reserva:
    reserva = ReservaRepository(db).obtener_por_id(reserva_id)
    if reserva is None:
        raise RecursoNoEncontrado(f"No existe una reserva con ID {reserva_id}.")
    return reserva


def actualizar_reserva(db: Session, reserva_id: int, data: ReservaCreate) -> Reserva:
    actual = obtener_reserva(db, reserva_id)
    sala = _validar_existencia_relacionada(db, data.usuario_id, data.sala_id)
    validar_sala_operativa(sala)
    validar_capacidad_sala(sala, data.num_asistentes)
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
    if reserva.estado == EstadoReserva.CANCELADA:
        raise ConflictoError("Una reserva cancelada no puede confirmarse.")

    repo = ReservaRepository(db)
    otras = [r for r in repo.listar() if r.id != reserva_id]
    validar_disponibilidad_sala(reserva.sala_id, reserva.fecha_inicio, reserva.fecha_fin, otras)

    # Regla de negocio 3: se invoca antes de confirmar. Si algún equipo de la
    # sala está dañado, la reserva no puede confirmarse.
    equipos = EquipamientoRepository(db).listar_por_sala(reserva.sala_id)
    validar_equipamiento_disponible(equipos)

    confirmada = replace(reserva, estado=EstadoReserva.CONFIRMADA)
    return repo.actualizar(confirmada)


def cancelar_reserva(db: Session, reserva_id: int) -> Reserva:
    reserva = obtener_reserva(db, reserva_id)
    if reserva.estado == EstadoReserva.CANCELADA:
        raise ConflictoError("La reserva ya está cancelada.")
    cancelada = replace(reserva, estado=EstadoReserva.CANCELADA)
    return ReservaRepository(db).actualizar(cancelada)


def eliminar_reserva(db: Session, reserva_id: int) -> None:
    obtener_reserva(db, reserva_id)  # lanza RecursoNoEncontrado si no existe
    ReservaRepository(db).eliminar(reserva_id)
