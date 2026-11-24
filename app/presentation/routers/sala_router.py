"""
Router de Sala: CRUD, consulta de equipamiento asociado y disponibilidad.
"""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.application.services import sala_service
from app.domain.entities import EstadoSala, Usuario
from app.presentation.dependencies import get_db, require_admin
from app.presentation.schemas.dtos import (
    DisponibilidadOut,
    EquipamientoOut,
    ErrorOut,
    EstadoSalaUpdate,
    SalaCreate,
    SalaDetalleOut,
    SalaOut,
    SalaPaginada,
)

router = APIRouter(prefix="/salas", tags=["Salas"])

ERR_422 = {"model": ErrorOut, "description": "Datos inválidos"}
ERR_404 = {"model": ErrorOut, "description": "La sala no existe"}
ERR_401 = {"model": ErrorOut, "description": "Falta el token o es inválido"}
ERR_403 = {"model": ErrorOut, "description": "Requiere rol administrador"}


@router.post(
    "",
    response_model=SalaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una sala",
    description="Registra una sala nueva. Queda en estado disponible. Requiere rol administrador.",
    responses={401: ERR_401, 403: ERR_403, 422: ERR_422},
)
def crear_sala(
    data: SalaCreate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    return sala_service.crear_sala(db, data)


@router.get(
    "",
    response_model=SalaPaginada,
    summary="Listar salas",
    description="Lista salas filtrando por estado, ordenando y paginando (en ese orden). "
    "Devuelve items, total, pagina, limite y total_paginas.",
    responses={422: ERR_422},
)
def listar_salas(
    estado: EstadoSala | None = Query(None, description="Filtra por estado de la sala"),
    ordenar_por: Literal["id", "nombre", "capacidad", "ubicacion", "estado"] = Query("id"),
    direccion: Literal["asc", "desc"] = Query("asc"),
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return sala_service.listar_salas(db, estado, ordenar_por, direccion, pagina, limite)


@router.get(
    "/{sala_id}/equipamientos",
    response_model=list[EquipamientoOut],
    summary="Listar el equipamiento de una sala",
    description="Devuelve todos los equipos asociados a la sala (relación 1:N).",
    responses={404: ERR_404, 422: ERR_422},
)
def listar_equipamiento_de_sala(sala_id: int, db: Session = Depends(get_db)):
    return sala_service.listar_equipamiento_de_sala(db, sala_id)


@router.get(
    "/{sala_id}/disponibilidad",
    response_model=DisponibilidadOut,
    summary="Consultar disponibilidad de una sala",
    description="Indica si la sala está libre en un rango horario, sin crear la reserva. "
    "Considera el estado de mantenimiento y las reservas confirmadas que se solapan.",
    responses={400: ERR_422, 404: ERR_404, 422: ERR_422},
)
def consultar_disponibilidad(
    sala_id: int,
    fecha_inicio: datetime = Query(description="Inicio del rango (ISO 8601)"),
    fecha_fin: datetime = Query(description="Fin del rango (ISO 8601)"),
    db: Session = Depends(get_db),
):
    return sala_service.consultar_disponibilidad(db, sala_id, fecha_inicio, fecha_fin)


@router.get(
    "/{sala_id}",
    response_model=SalaDetalleOut,
    summary="Obtener una sala por ID",
    description="Devuelve la sala indicada junto con su equipamiento asociado.",
    responses={404: ERR_404, 422: ERR_422},
)
def obtener_sala(sala_id: int, db: Session = Depends(get_db)):
    datos = sala_service.obtener_sala_con_equipamiento(db, sala_id)
    return {**datos["sala"].__dict__, "equipamientos": datos["equipamientos"]}


@router.put(
    "/{sala_id}",
    response_model=SalaOut,
    summary="Actualizar una sala",
    description="Reemplaza nombre, capacidad y ubicación. El estado se conserva. "
    "Requiere rol administrador.",
    responses={401: ERR_401, 403: ERR_403, 404: ERR_404, 422: ERR_422},
)
def actualizar_sala(
    sala_id: int,
    data: SalaCreate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    return sala_service.actualizar_sala(db, sala_id, data)


@router.patch(
    "/{sala_id}/estado",
    response_model=SalaOut,
    summary="Cambiar el estado de una sala",
    description="Pasa la sala a disponible o mantenimiento. Requiere rol administrador.",
    responses={401: ERR_401, 403: ERR_403, 404: ERR_404, 422: ERR_422},
)
def cambiar_estado_sala(
    sala_id: int,
    data: EstadoSalaUpdate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    return sala_service.cambiar_estado_sala(db, sala_id, data.estado)


@router.delete(
    "/{sala_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una sala",
    description="Elimina la sala. Si tiene reservas asociadas responde 409. "
    "Requiere rol administrador.",
    responses={
        401: ERR_401,
        403: ERR_403,
        404: ERR_404,
        409: {"model": ErrorOut, "description": "La sala tiene reservas asociadas"},
    },
)
def eliminar_sala(
    sala_id: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    sala_service.eliminar_sala(db, sala_id)
