"""
Casos de uso de Sala: lógica de negocio y coordinación con el repositorio.
"""
import math
from typing import Optional, Literal

from app.domain.entities import Sala, EstadoSala
from app.infrastructure.repositories.sala_repository import sala_store
from app.presentation.schemas.dtos import SalaCreate


def crear_sala(data: SalaCreate) -> Sala:
    return sala_store.add(
        lambda nuevo_id: Sala(
            id=nuevo_id,
            nombre=data.nombre,
            capacidad=data.capacidad,
            ubicacion=data.ubicacion,
            estado=EstadoSala.DISPONIBLE,
        )
    )


def listar_salas(
    estado: Optional[EstadoSala] = None,
    ordenar_por: str = "id",
    direccion: str = "asc",
    pagina: int = 1,
    limite: int = 20,
) -> dict:
    salas = sala_store.list_all()

    if estado is not None:
        salas = [s for s in salas if s.estado == estado]

    reverse = direccion == "desc"
    salas = sorted(salas, key=lambda s: getattr(s, ordenar_por), reverse=reverse)

    total = len(salas)
    inicio = (pagina - 1) * limite
    fin = inicio + limite
    items = salas[inicio:fin]
    total_paginas = math.ceil(total / limite) if limite > 0 else 0

    return {
        "items": items,
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "total_paginas": total_paginas,
    }


def obtener_sala(sala_id: int) -> Sala:
    sala = sala_store.get(sala_id)
    if sala is None:
        raise ValueError(f"No existe una sala con ID {sala_id}.")
    return sala


def actualizar_sala(sala_id: int, data: SalaCreate) -> Sala:
    sala_existente = obtener_sala(sala_id)
    sala_actualizada = Sala(
        id=sala_id,
        nombre=data.nombre,
        capacidad=data.capacidad,
        ubicacion=data.ubicacion,
        estado=sala_existente.estado,
    )
    sala_store.update(sala_id, sala_actualizada)
    return sala_actualizada


def eliminar_sala(sala_id: int) -> None:
    obtener_sala(sala_id)  # valida que exista, lanza ValueError si no
    sala_store.delete(sala_id)