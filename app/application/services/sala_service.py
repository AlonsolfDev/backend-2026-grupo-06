"""
Casos de uso de Sala: lógica de negocio y coordinación con el repositorio.
"""

import math
from dataclasses import replace
from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.entities import EstadoReserva, EstadoSala, Sala
from app.domain.errores import ConflictoError, RecursoNoEncontrado
from app.domain.reglas_negocio import validar_fechas_reserva
from app.infrastructure.repositories.equipamiento_repository import EquipamientoRepository
from app.infrastructure.repositories.reserva_repository import ReservaRepository
from app.infrastructure.repositories.sala_repository import SalaRepository
from app.presentation.schemas.dtos import SalaCreate


def crear_sala(db: Session, data: SalaCreate) -> Sala:
    nueva = Sala(
        id=0,  # el repositorio asigna el ID real
        nombre=data.nombre,
        capacidad=data.capacidad,
        ubicacion=data.ubicacion,
        estado=EstadoSala.DISPONIBLE,
    )
    return SalaRepository(db).crear(nueva)


def listar_salas(
    db: Session,
    estado: EstadoSala | None = None,
    ordenar_por: str = "id",
    direccion: str = "asc",
    pagina: int = 1,
    limite: int = 20,
) -> dict:
    # El repositorio filtra, ordena y pagina en la base de datos (en ese orden)
    items, total = SalaRepository(db).listar_paginado(
        estado, ordenar_por, direccion, pagina, limite
    )
    total_paginas = math.ceil(total / limite) if total > 0 else 0

    return {
        "items": items,
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "total_paginas": total_paginas,
    }


def obtener_sala(db: Session, sala_id: int) -> Sala:
    sala = SalaRepository(db).obtener_por_id(sala_id)
    if sala is None:
        raise RecursoNoEncontrado(f"No existe una sala con ID {sala_id}.")
    return sala


def obtener_sala_con_equipamiento(db: Session, sala_id: int) -> dict:
    """Devuelve la sala y su equipamiento (relación 1:N)."""
    sala = obtener_sala(db, sala_id)
    equipos = EquipamientoRepository(db).listar_por_sala(sala_id)
    return {"sala": sala, "equipamientos": equipos}


def listar_equipamiento_de_sala(db: Session, sala_id: int):
    obtener_sala(db, sala_id)
    return EquipamientoRepository(db).listar_por_sala(sala_id)


def consultar_disponibilidad(
    db: Session, sala_id: int, fecha_inicio: datetime, fecha_fin: datetime
) -> dict:
    """Responde si la sala está libre en un rango horario, sin crear la reserva."""
    sala = obtener_sala(db, sala_id)
    validar_fechas_reserva(fecha_inicio, fecha_fin)

    if sala.estado == EstadoSala.MANTENIMIENTO:
        return {
            "sala_id": sala_id,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "disponible": False,
            "motivo": "La sala está en mantenimiento.",
        }

    for reserva in ReservaRepository(db).listar_por_sala(sala_id):
        if reserva.estado != EstadoReserva.CONFIRMADA:
            continue
        se_solapan = fecha_inicio < reserva.fecha_fin and fecha_fin > reserva.fecha_inicio
        if se_solapan:
            return {
                "sala_id": sala_id,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "disponible": False,
                "motivo": (
                    "La sala ya tiene una reserva confirmada en ese horario "
                    f"(reserva {reserva.id})."
                ),
            }

    return {
        "sala_id": sala_id,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "disponible": True,
        "motivo": "La sala está disponible en el horario solicitado.",
    }


def actualizar_sala(db: Session, sala_id: int, data: SalaCreate) -> Sala:
    existente = obtener_sala(db, sala_id)
    actualizada = replace(
        existente,
        nombre=data.nombre,
        capacidad=data.capacidad,
        ubicacion=data.ubicacion,
        # el estado se conserva al actualizar datos básicos
    )
    return SalaRepository(db).actualizar(actualizada)


def cambiar_estado_sala(db: Session, sala_id: int, nuevo_estado: EstadoSala) -> Sala:
    sala = obtener_sala(db, sala_id)
    return SalaRepository(db).actualizar(replace(sala, estado=nuevo_estado))


def eliminar_sala(db: Session, sala_id: int) -> None:
    obtener_sala(db, sala_id)  # lanza RecursoNoEncontrado si no existe
    # Integridad de referencias: no se borra una sala que tiene reservas
    if ReservaRepository(db).listar_por_sala(sala_id):
        raise ConflictoError(
            f"No se puede eliminar la sala {sala_id} porque tiene reservas asociadas."
        )
    SalaRepository(db).eliminar(sala_id)
