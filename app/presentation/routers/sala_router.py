"""
Router de Sala: define las URIs y delega la lógica al service.
"""
from typing import Optional, Literal

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.domain.entities import EstadoSala
from app.presentation.dependencies import get_db
from app.presentation.schemas.dtos import ErrorOut, SalaCreate, SalaOut, SalaPaginada
from app.application.services import sala_service

router = APIRouter(prefix="/salas", tags=["Salas"])

ERR_422 = {"model": ErrorOut, "description": "Datos inválidos"}
ERR_404 = {"model": ErrorOut, "description": "La sala no existe"}


@router.post(
    "",
    response_model=SalaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una sala",
    description="Registra una sala nueva. Queda en estado disponible.",
    responses={422: ERR_422},
)
def crear_sala(data: SalaCreate, db: Session = Depends(get_db)):
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
    estado: Optional[EstadoSala] = Query(None, description="Filtra por estado de la sala"),
    ordenar_por: Literal["id", "nombre", "capacidad", "ubicacion", "estado"] = Query("id"),
    direccion: Literal["asc", "desc"] = Query("asc"),
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return sala_service.listar_salas(db, estado, ordenar_por, direccion, pagina, limite)


@router.get(
    "/{sala_id}",
    response_model=SalaOut,
    summary="Obtener una sala por ID",
    description="Devuelve la sala indicada.",
    responses={404: ERR_404, 422: ERR_422},
)
def obtener_sala(sala_id: int, db: Session = Depends(get_db)):
    return sala_service.obtener_sala(db, sala_id)


@router.put(
    "/{sala_id}",
    response_model=SalaOut,
    summary="Actualizar una sala",
    description="Reemplaza nombre, capacidad y ubicación. El estado se conserva.",
    responses={404: ERR_404, 422: ERR_422},
)
def actualizar_sala(sala_id: int, data: SalaCreate, db: Session = Depends(get_db)):
    return sala_service.actualizar_sala(db, sala_id, data)


@router.delete(
    "/{sala_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una sala",
    description="Elimina la sala. Si tiene reservas asociadas responde 409.",
    responses={
        404: ERR_404,
        409: {"model": ErrorOut, "description": "La sala tiene reservas asociadas"},
    },
)
def eliminar_sala(sala_id: int, db: Session = Depends(get_db)):
    sala_service.eliminar_sala(db, sala_id)