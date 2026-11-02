"""
Router de Usuario: define las URIs y delega la lógica al service.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.presentation.dependencies import get_db
from app.presentation.schemas.dtos import ErrorOut, UsuarioCreate, UsuarioOut
from app.application.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

ERR_422 = {"model": ErrorOut, "description": "Datos inválidos"}


@router.post(
    "",
    response_model=UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un usuario",
    description="Registra un usuario. El correo debe ser único.",
    responses={
        409: {"model": ErrorOut, "description": "Ya existe un usuario con ese correo"},
        422: ERR_422,
    },
)
def crear_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    return usuario_service.crear_usuario(db, data)


@router.get(
    "",
    response_model=list[UsuarioOut],
    summary="Listar usuarios",
    description="Devuelve todos los usuarios registrados.",
)
def listar_usuarios(db: Session = Depends(get_db)):
    return usuario_service.listar_usuarios(db)


@router.get(
    "/{usuario_id}",
    response_model=UsuarioOut,
    summary="Obtener un usuario por ID",
    description="Devuelve el usuario indicado.",
    responses={
        404: {"model": ErrorOut, "description": "El usuario no existe"},
        422: ERR_422,
    },
)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return usuario_service.obtener_usuario(db, usuario_id)