"""
Router de Equipamiento: define las URIs y delega la lógica al service.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.domain.entities import EstadoEquipamiento
from app.presentation.dependencies import get_db
from app.presentation.schemas.dtos import EquipamientoCreate, EquipamientoOut, ErrorOut
from app.application.services import equipamiento_service

router = APIRouter(prefix="/equipamientos", tags=["Equipamientos"])

ERR_422 = {"model": ErrorOut, "description": "Datos inválidos"}
ERR_404 = {"model": ErrorOut, "description": "El equipamiento o la sala no existe"}


@router.post(
    "",
    response_model=EquipamientoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear equipamiento",
    description="Registra un equipo asociado a una sala existente. Queda disponible.",
    responses={404: ERR_404, 422: ERR_422},
)
def crear_equipamiento(data: EquipamientoCreate, db: Session = Depends(get_db)):
    return equipamiento_service.crear_equipamiento(db, data)


@router.get(
    "",
    response_model=list[EquipamientoOut],
    summary="Listar equipamientos",
    description="Devuelve todo el equipamiento registrado.",
)
def listar_equipamientos(db: Session = Depends(get_db)):
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
    description="Cambia el estado del equipo (disponible o danado).",
    responses={404: ERR_404, 422: ERR_422},
)
def actualizar_estado_equipamiento(
    equipamiento_id: int,
    nuevo_estado: EstadoEquipamiento,
    db: Session = Depends(get_db),
):
    return equipamiento_service.actualizar_estado_equipamiento(db, equipamiento_id, nuevo_estado)