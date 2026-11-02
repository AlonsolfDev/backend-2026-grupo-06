"""
Router de Reserva: define las URIs, incluyendo CRUD completo y el
listado con filtrado + ordenamiento + paginación.
"""
from typing import Optional, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.presentation.dependencies import get_db
from app.presentation.schemas.dtos import ErrorOut, ReservaCreate, ReservaOut, ReservaPaginada
from app.application.services import reserva_service

router = APIRouter(prefix="/reservas", tags=["Reservas"])

ERR_422 = {"model": ErrorOut, "description": "Datos inválidos"}
ERR_404 = {"model": ErrorOut, "description": "La reserva, el usuario o la sala no existe"}
ERR_400 = {"model": ErrorOut, "description": "Se viola una regla de negocio"}
ERR_409 = {"model": ErrorOut, "description": "La sala ya tiene una reserva confirmada en ese horario"}


@router.post(
    "",
    response_model=ReservaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una reserva",
    description="Crea una reserva pendiente. Valida que existan el usuario y la sala, "
    "que las fechas sean coherentes y que no se solape con una reserva confirmada.",
    responses={400: ERR_400, 404: ERR_404, 409: ERR_409, 422: ERR_422},
)
def crear_reserva(data: ReservaCreate, db: Session = Depends(get_db)):
    return reserva_service.crear_reserva(db, data)


@router.get(
    "",
    response_model=ReservaPaginada,
    summary="Listar reservas",
    description="Lista reservas filtrando por sala, ordenando y paginando (en ese orden). "
    "Devuelve items, total, pagina, limite y total_paginas.",
    responses={422: ERR_422},
)
def listar_reservas(
    sala_id: Optional[int] = Query(None, description="Filtra por sala"),
    ordenar_por: Literal["id", "fecha_inicio", "fecha_fin", "estado"] = Query("fecha_inicio"),
    direccion: Literal["asc", "desc"] = Query("asc"),
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return reserva_service.listar_reservas_paginado(
        db, sala_id, ordenar_por, direccion, pagina, limite
    )


@router.get(
    "/{reserva_id}",
    response_model=ReservaOut,
    summary="Obtener una reserva por ID",
    description="Devuelve la reserva indicada.",
    responses={404: ERR_404, 422: ERR_422},
)
def obtener_reserva(reserva_id: int, db: Session = Depends(get_db)):
    return reserva_service.obtener_reserva(db, reserva_id)


@router.put(
    "/{reserva_id}",
    response_model=ReservaOut,
    summary="Actualizar una reserva",
    description="Reemplaza los datos de la reserva. El estado se conserva.",
    responses={400: ERR_400, 404: ERR_404, 409: ERR_409, 422: ERR_422},
)
def actualizar_reserva(reserva_id: int, data: ReservaCreate, db: Session = Depends(get_db)):
    return reserva_service.actualizar_reserva(db, reserva_id, data)


@router.patch(
    "/{reserva_id}/confirmar",
    response_model=ReservaOut,
    summary="Confirmar una reserva",
    description="Pasa la reserva a confirmada si la sala no tiene otra confirmada en ese horario.",
    responses={404: ERR_404, 409: ERR_409},
)
def confirmar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    return reserva_service.confirmar_reserva(db, reserva_id)


@router.delete(
    "/{reserva_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una reserva",
    description="Elimina la reserva indicada.",
    responses={404: ERR_404},
)
def eliminar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva_service.eliminar_reserva(db, reserva_id)