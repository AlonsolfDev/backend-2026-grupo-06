"""
Router de Reserva: define las URIs, incluyendo CRUD completo y el
listado con filtrado + ordenamiento + paginación.
"""
from typing import Optional, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.presentation.dependencies import get_db
from app.presentation.schemas.dtos import ReservaCreate, ReservaOut, ReservaPaginada
from app.application.services import reserva_service

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.post("", response_model=ReservaOut, status_code=status.HTTP_201_CREATED)
def crear_reserva(data: ReservaCreate, db: Session = Depends(get_db)):
    return reserva_service.crear_reserva(db, data)


@router.get("", response_model=ReservaPaginada)
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


@router.get("/{reserva_id}", response_model=ReservaOut)
def obtener_reserva(reserva_id: int, db: Session = Depends(get_db)):
    return reserva_service.obtener_reserva(db, reserva_id)


@router.put("/{reserva_id}", response_model=ReservaOut)
def actualizar_reserva(reserva_id: int, data: ReservaCreate, db: Session = Depends(get_db)):
    return reserva_service.actualizar_reserva(db, reserva_id, data)


@router.patch("/{reserva_id}/confirmar", response_model=ReservaOut)
def confirmar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    return reserva_service.confirmar_reserva(db, reserva_id)


@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    reserva_service.eliminar_reserva(db, reserva_id)