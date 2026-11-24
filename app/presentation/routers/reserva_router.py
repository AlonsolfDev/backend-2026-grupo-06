"""
Router de Reserva: CRUD completo, confirmación, cancelación y listado con
filtrado combinado + ordenamiento + paginación.

Autorización:
- Cualquiera puede consultar disponibilidad y listar reservas.
- Un usuario autenticado crea reservas a su nombre y solo modifica las suyas.
- El administrador puede operar sobre cualquier reserva.
"""

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.application.services import reserva_service
from app.domain.entities import EstadoReserva, RolUsuario, Usuario
from app.domain.errores import Prohibido
from app.presentation.dependencies import get_current_user, get_db
from app.presentation.schemas.dtos import (
    ErrorOut,
    ReservaCreate,
    ReservaOut,
    ReservaPaginada,
)

router = APIRouter(prefix="/reservas", tags=["Reservas"])

ERR_422 = {"model": ErrorOut, "description": "Datos inválidos"}
ERR_404 = {"model": ErrorOut, "description": "La reserva, el usuario o la sala no existe"}
ERR_400 = {"model": ErrorOut, "description": "Se viola una regla de negocio"}
ERR_409 = {"model": ErrorOut, "description": "Conflicto con el estado actual"}
ERR_401 = {"model": ErrorOut, "description": "Falta el token o es inválido"}
ERR_403 = {"model": ErrorOut, "description": "No puedes operar sobre una reserva ajena"}


def _autorizar_propietario(usuario: Usuario, reserva) -> None:
    if usuario.rol != RolUsuario.ADMINISTRADOR and reserva.usuario_id != usuario.id:
        raise Prohibido("Solo puedes modificar tus propias reservas.")


@router.post(
    "",
    response_model=ReservaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una reserva",
    description="Crea una reserva pendiente. Valida existencia de usuario y sala, "
    "que la sala no esté en mantenimiento, la capacidad, las fechas y el solapamiento. "
    "Un usuario no administrador solo puede reservar a su propio nombre.",
    responses={400: ERR_400, 401: ERR_401, 403: ERR_403, 404: ERR_404, 409: ERR_409, 422: ERR_422},
)
def crear_reserva(
    data: ReservaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if usuario.rol != RolUsuario.ADMINISTRADOR:
        data = data.model_copy(update={"usuario_id": usuario.id})
    return reserva_service.crear_reserva(db, data)


@router.get(
    "",
    response_model=ReservaPaginada,
    summary="Listar reservas",
    description="Lista reservas con filtros combinables por usuario, sala, estado y "
    "fecha del día, ordenando y paginando. Devuelve items, total, pagina, limite y total_paginas.",
    responses={422: ERR_422},
)
def listar_reservas(
    usuario_id: int | None = Query(None, description="Filtra por usuario"),
    sala_id: int | None = Query(None, description="Filtra por sala"),
    estado: EstadoReserva | None = Query(None, description="Filtra por estado"),
    fecha: date | None = Query(None, description="Filtra por fecha de inicio (AAAA-MM-DD)"),
    ordenar_por: Literal["id", "fecha_inicio", "fecha_fin", "estado"] = Query("fecha_inicio"),
    direccion: Literal["asc", "desc"] = Query("asc"),
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return reserva_service.listar_reservas_paginado(
        db, usuario_id, sala_id, estado, fecha, ordenar_por, direccion, pagina, limite
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
    responses={400: ERR_400, 401: ERR_401, 403: ERR_403, 404: ERR_404, 409: ERR_409, 422: ERR_422},
)
def actualizar_reserva(
    reserva_id: int,
    data: ReservaCreate,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    existente = reserva_service.obtener_reserva(db, reserva_id)
    _autorizar_propietario(usuario, existente)
    if usuario.rol != RolUsuario.ADMINISTRADOR:
        data = data.model_copy(update={"usuario_id": usuario.id})
    return reserva_service.actualizar_reserva(db, reserva_id, data)


@router.patch(
    "/{reserva_id}/confirmar",
    response_model=ReservaOut,
    summary="Confirmar una reserva",
    description="Pasa la reserva a confirmada si la sala no tiene otra confirmada en ese "
    "horario y no tiene equipamiento dañado (regla de negocio 3).",
    responses={400: ERR_400, 401: ERR_401, 403: ERR_403, 404: ERR_404, 409: ERR_409},
)
def confirmar_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    existente = reserva_service.obtener_reserva(db, reserva_id)
    _autorizar_propietario(usuario, existente)
    return reserva_service.confirmar_reserva(db, reserva_id)


@router.patch(
    "/{reserva_id}/cancelar",
    response_model=ReservaOut,
    summary="Cancelar una reserva",
    description="Pasa la reserva a cancelada. Una reserva ya cancelada responde 409.",
    responses={401: ERR_401, 403: ERR_403, 404: ERR_404, 409: ERR_409},
)
def cancelar_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    existente = reserva_service.obtener_reserva(db, reserva_id)
    _autorizar_propietario(usuario, existente)
    return reserva_service.cancelar_reserva(db, reserva_id)


@router.delete(
    "/{reserva_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una reserva",
    description="Elimina la reserva indicada.",
    responses={401: ERR_401, 403: ERR_403, 404: ERR_404},
)
def eliminar_reserva(
    reserva_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    existente = reserva_service.obtener_reserva(db, reserva_id)
    _autorizar_propietario(usuario, existente)
    reserva_service.eliminar_reserva(db, reserva_id)
