"""
Router de Sala: define las URIs y delega la lógica al service.
"""
from typing import Optional, Literal

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.domain.entities import EstadoSala
from app.presentation.dependencies import get_db
from app.presentation.schemas.dtos import SalaCreate, SalaOut, SalaPaginada
from app.application.services import sala_service

router = APIRouter(prefix="/salas", tags=["Salas"])


@router.post("", response_model=SalaOut, status_code=status.HTTP_201_CREATED)
def crear_sala(data: SalaCreate, db: Session = Depends(get_db)):
    return sala_service.crear_sala(db, data)


@router.get("", response_model=SalaPaginada)
def listar_salas(
    estado: Optional[EstadoSala] = Query(None, description="Filtra por estado de la sala"),
    ordenar_por: Literal["id", "nombre", "capacidad", "ubicacion", "estado"] = Query("id"),
    direccion: Literal["asc", "desc"] = Query("asc"),
    pagina: int = Query(1, ge=1),
    limite: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return sala_service.listar_salas(db, estado, ordenar_por, direccion, pagina, limite)


@router.get("/{sala_id}", response_model=SalaOut)
def obtener_sala(sala_id: int, db: Session = Depends(get_db)):
    return sala_service.obtener_sala(db, sala_id)


@router.put("/{sala_id}", response_model=SalaOut)
def actualizar_sala(sala_id: int, data: SalaCreate, db: Session = Depends(get_db)):
    return sala_service.actualizar_sala(db, sala_id, data)


@router.delete("/{sala_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_sala(sala_id: int, db: Session = Depends(get_db)):
    sala_service.eliminar_sala(db, sala_id)