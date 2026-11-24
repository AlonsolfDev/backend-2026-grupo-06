"""
Router de Equipamiento: define las URIs y delega la lógica al service.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.application.services import equipamiento_service
from app.domain.entities import Usuario
from app.presentation.dependencies import get_db, require_admin
from app.presentation.schemas.dtos import (
    EquipamientoCreate,
    EquipamientoOut,
    ErrorOut,
    EstadoEquipamientoUpdate,
)

router = APIRouter(prefix="/equipamientos", tags=["Equipamientos"])

ERR_422 = {"model": ErrorOut, "description": "Datos inválidos"}
ERR_404 = {"model": ErrorOut, "description": "El equipamiento o la sala no existe"}
ERR_401 = {"model": ErrorOut, "description": "Falta el token o es inválido"}
ERR_403 = {"model": ErrorOut, "description": "Requiere rol administrador"}


@router.post(
    "",
    response_model=EquipamientoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear equipamiento",
    description="Registra un equipo asociado a una sala existente. Queda disponible. "
    "Requiere rol administrador.",
    responses={401: ERR_401, 403: ERR_403, 404: ERR_404, 422: ERR_422},
)
def crear_equipamiento(
    data: EquipamientoCreate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    return equipamiento_service.crear_equipamiento(db, data)


@router.get(
    "",
    response_model=list[EquipamientoOut],
    summary="Listar equipamientos",
    description="Devuelve el equipamiento registrado. Se puede filtrar por sala.",
)
def listar_equipamientos(
    sala_id: int | None = Query(None, description="Filtra por sala"),
    db: Session = Depends(get_db),
):
    if sala_id is not None:
        return equipamiento_service.listar_equipamientos_por_sala(db, sala_id)
    return equipamiento_service.listar_equipamientos(db)


@router.get(
    "/{equipamiento_id}",
    response_model=EquipamientoOut,
    summary="Obtener equipamiento por ID",
    description="Devuelve el equipo indicado.",
    responses={404: ERR_404, 422: ERR_422},
)
def obtener_equipamiento(equipamiento_id: int, db: Session = Depends(get_db)):
    return equipamiento_service.obtener_equipamiento(db, equipamiento_id)


@router.patch(
    "/{equipamiento_id}/estado",
    response_model=EquipamientoOut,
    summary="Actualizar el estado de un equipo",
    description="Cambia el estado del equipo (disponible o danado). Requiere rol administrador.",
    responses={401: ERR_401, 403: ERR_403, 404: ERR_404, 422: ERR_422},
)
def actualizar_estado_equipamiento(
    equipamiento_id: int,
    data: EstadoEquipamientoUpdate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    return equipamiento_service.actualizar_estado_equipamiento(db, equipamiento_id, data.estado)


@router.delete(
    "/{equipamiento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un equipo",
    description="Elimina el equipamiento indicado. Requiere rol administrador.",
    responses={401: ERR_401, 403: ERR_403, 404: ERR_404},
)
def eliminar_equipamiento(
    equipamiento_id: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    equipamiento_service.eliminar_equipamiento(db, equipamiento_id)
