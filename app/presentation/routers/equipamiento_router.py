"""
Router de Equipamiento: define las URIs y delega la lógica al service.
"""
from fastapi import APIRouter, status

from app.domain.entities import EstadoEquipamiento
from app.presentation.schemas.dtos import EquipamientoCreate, EquipamientoOut
from app.application.services import equipamiento_service

router = APIRouter(prefix="/equipamientos", tags=["Equipamientos"])


@router.post("", response_model=EquipamientoOut, status_code=status.HTTP_201_CREATED)
def crear_equipamiento(data: EquipamientoCreate):
    return equipamiento_service.crear_equipamiento(data)


@router.get("", response_model=list[EquipamientoOut])
def listar_equipamientos():
    return equipamiento_service.listar_equipamientos()


@router.get("/{equipamiento_id}", response_model=EquipamientoOut)
def obtener_equipamiento(equipamiento_id: int):
    return equipamiento_service.obtener_equipamiento(equipamiento_id)


@router.patch("/{equipamiento_id}/estado", response_model=EquipamientoOut)
def actualizar_estado_equipamiento(equipamiento_id: int, nuevo_estado: EstadoEquipamiento):
    return equipamiento_service.actualizar_estado_equipamiento(equipamiento_id, nuevo_estado)