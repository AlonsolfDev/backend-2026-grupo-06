"""
Router de Reserva: define las URIs, incluyendo CRUD completo y el
listado con filtrado + ordenamiento + paginación.
"""
import math
from typing import Optional, Literal

from fastapi import APIRouter, status

from app.presentation.schemas.dtos import ReservaCreate, ReservaOut
from app.application.services import reserva_service

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.post("", response_model=ReservaOut, status_code=status.HTTP_201_CREATED)
def crear_reserva(data: ReservaCreate):
    return reserva_service.crear_reserva(data)


@router.get("")
def listar_reservas(
    sala_id: Optional[int] = None,
    ordenar_por: Literal["fecha_inicio", "fecha_fin"] = "fecha_inicio",
    direccion: Literal["asc", "desc"] = "asc",
    pagina: int = 1,
    limite: int = 20,
):
    # 1. Filtrado
    reservas = reserva_service.listar_reservas()
    if sala_id is not None:
        reservas = [r for r in reservas if r.sala_id == sala_id]

    # 2. Ordenamiento
    reservas.sort(
        key=lambda r: getattr(r, ordenar_por),
        reverse=(direccion == "desc"),
    )

    # 3. Paginación
    total = len(reservas)
    total_paginas = math.ceil(total / limite) if total > 0 else 0
    inicio = (pagina - 1) * limite
    fin = inicio + limite
    items = reservas[inicio:fin]

    return {
        "items": [ReservaOut.model_validate(r, from_attributes=True) for r in items],
        "total": total,
        "pagina": pagina,
        "limite": limite,
        "total_paginas": total_paginas,
    }


@router.get("/{reserva_id}", response_model=ReservaOut)
def obtener_reserva(reserva_id: int):
    return reserva_service.obtener_reserva(reserva_id)


@router.put("/{reserva_id}", response_model=ReservaOut)
def actualizar_reserva(reserva_id: int, data: ReservaCreate):
    return reserva_service.actualizar_reserva(reserva_id, data)


@router.patch("/{reserva_id}/confirmar", response_model=ReservaOut)
def confirmar_reserva(reserva_id: int):
    return reserva_service.confirmar_reserva(reserva_id)


@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_reserva(reserva_id: int):
    reserva_service.eliminar_reserva(reserva_id)