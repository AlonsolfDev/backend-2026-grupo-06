"""
Router de Usuario: define las URIs y delega la lógica al service.
"""
from fastapi import APIRouter, status

from app.presentation.schemas.dtos import UsuarioCreate, UsuarioOut
from app.application.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(data: UsuarioCreate):
    return usuario_service.crear_usuario(data)


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios():
    return usuario_service.listar_usuarios()


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obtener_usuario(usuario_id: int):
    return usuario_service.obtener_usuario(usuario_id)