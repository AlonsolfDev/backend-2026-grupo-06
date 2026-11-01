"""
Router de Equipamiento: define las URIs y delega la lógica al service.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.domain.entities import EstadoEquipamiento
from app.presentation.dependencies import get_db
from app.presentation.schemas.dtos import EquipamientoCreate, EquipamientoOut
from app.application.services import equipamiento_service

router = APIRouter(prefix="/equipamientos", tags=["Equipamientos"])


@router.post("", response_model=EquipamientoOut, status_code=status.HTTP_201_CREATED)
def crear_equipamiento(data: EquipamientoCreate, db: Session = Depends(get_db)):
    return equipamiento_service.crear_equipamiento(db, data)


@router.get("", response_model=list[EquipamientoOut])
def listar_equipamientos(db: Session = Depends(get_db)):
    return equipamiento_service.listar_equipamientos(db)


@router.get("/{equipamiento_id}", response_model=EquipamientoOut)
def obtener_equipamiento(equipamiento_id: int, db: Session = Depends(get_db)):
    return equipamiento_service.obtener_equipamiento(db, equipamiento_id)


@router.patch("/{equipamiento_id}/estado", response_model=EquipamientoOut)
def actualizar_estado_equipamiento(
    equipamiento_id: int,
    nuevo_estado: EstadoEquipamiento,
    db: Session = Depends(get_db),
):
    return equipamiento_service.actualizar_estado_equipamiento(db, equipamiento_id, nuevo_estado)