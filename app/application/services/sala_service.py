"""
Casos de uso de Sala: lógica de negocio y coordinación con el repositorio.
"""
import math
from dataclasses import replace
from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities import Sala, EstadoSala
from app.domain.errores import ConflictoError, RecursoNoEncontrado
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
    estado: Optional[EstadoSala] = None,
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


def eliminar_sala(db: Session, sala_id: int) -> None:
    obtener_sala(db, sala_id)  # lanza RecursoNoEncontrado si no existe
    # Integridad de referencias: no se borra una sala que tiene reservas
    if ReservaRepository(db).listar_por_sala(sala_id):
        raise ConflictoError(
            f"No se puede eliminar la sala {sala_id} porque tiene reservas asociadas."
        )
    SalaRepository(db).eliminar(sala_id)