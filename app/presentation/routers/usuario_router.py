"""
Router de Usuario: define las URIs y delega la lógica al service.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.presentation.dependencies import get_db
from app.presentation.schemas.dtos import UsuarioCreate, UsuarioOut
from app.application.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    return usuario_service.crear_usuario(db, data)


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    return usuario_service.listar_usuarios(db)


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return usuario_service.obtener_usuario(db, usuario_id)