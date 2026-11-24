"""
Router de Usuario: define las URIs y delega la lógica al service.
La gestión de cuentas queda reservada al rol administrador.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.services import usuario_service
from app.domain.entities import Usuario
from app.domain.errores import Prohibido
from app.presentation.dependencies import get_current_user, get_db, require_admin
from app.presentation.schemas.dtos import ErrorOut, RolUpdate, UsuarioCreate, UsuarioOut

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

ERR_422 = {"model": ErrorOut, "description": "Datos inválidos"}
ERR_401 = {"model": ErrorOut, "description": "Falta el token o es inválido"}
ERR_403 = {"model": ErrorOut, "description": "Requiere rol administrador"}


@router.post(
    "",
    response_model=UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un usuario",
    description="Registra un usuario con rol y contraseña. El correo debe ser único. "
    "Requiere rol administrador.",
    responses={
        401: ERR_401,
        403: ERR_403,
        409: {"model": ErrorOut, "description": "Ya existe un usuario con ese correo"},
        422: ERR_422,
    },
)
def crear_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    return usuario_service.crear_usuario(db, data)


@router.get(
    "",
    response_model=list[UsuarioOut],
    summary="Listar usuarios",
    description="Devuelve todos los usuarios registrados. Requiere rol administrador.",
    responses={401: ERR_401, 403: ERR_403},
)
def listar_usuarios(db: Session = Depends(get_db), _admin: Usuario = Depends(require_admin)):
    return usuario_service.listar_usuarios(db)


@router.get(
    "/{usuario_id}",
    response_model=UsuarioOut,
    summary="Obtener un usuario por ID",
    description="Un administrador puede consultar cualquiera; un usuario, solo su propio perfil.",
    responses={
        401: ERR_401,
        403: ERR_403,
        404: {"model": ErrorOut, "description": "El usuario no existe"},
        422: ERR_422,
    },
)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    actual: Usuario = Depends(get_current_user),
):
    if actual.rol.value != "administrador" and actual.id != usuario_id:
        raise Prohibido("Solo puedes consultar tu propio perfil.")
    return usuario_service.obtener_usuario(db, usuario_id)


@router.patch(
    "/{usuario_id}/rol",
    response_model=UsuarioOut,
    summary="Cambiar el rol de un usuario",
    description="Solo un administrador puede ascender o cambiar el rol de otra cuenta.",
    responses={
        401: ERR_401,
        403: ERR_403,
        404: {"model": ErrorOut, "description": "El usuario no existe"},
        422: ERR_422,
    },
)
def cambiar_rol(
    usuario_id: int,
    data: RolUpdate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    return usuario_service.cambiar_rol(db, usuario_id, data.rol)
