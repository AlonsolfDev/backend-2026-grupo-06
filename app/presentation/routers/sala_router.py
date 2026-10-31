"""
Router de Sala: define las URIs y delega la lógica al service.
"""
from typing import Optional, Literal

from fastapi import APIRouter, status, Query

from app.domain.entities import EstadoSala
from app.presentation.schemas.dtos import SalaCreate, SalaOut, SalaPaginada
from app.application.services import sala_service

router = APIRouter(prefix="/salas", tags=["Salas"])


@router.post("", response_model=SalaOut, status_code=status.HTTP_201_CREATED)
def crear_sala(data: SalaCreate):
    return sala_service.crear_sala(data)


@router.get("", response_model=SalaPaginada)
def listar_salas(
    estado: Optional[EstadoSala] = Query(None, description="Filtra por estado de la sala"),
    ordenar_por: Literal["id", "nombre", "capacidad", "ubicacion", "estado"] = Query("id"),
    direccion: Literal["asc", "desc"] = Query("asc"),
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
):
    return sala_service.listar_salas(estado, ordenar_por, direccion, pagina, limite)


@router.get("/{sala_id}", response_model=SalaOut)
def obtener_sala(sala_id: int):
    return sala_service.obtener_sala(sala_id)


@router.put("/{sala_id}", response_model=SalaOut)
def actualizar_sala(sala_id: int, data: SalaCreate):
    return sala_service.actualizar_sala(sala_id, data)


@router.delete("/{sala_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_sala(sala_id: int):
    sala_service.eliminar_sala(sala_id)