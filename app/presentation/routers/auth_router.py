"""
Router de autenticación: registro, login, refresco, logout, perfil y
recuperación de contraseña.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.services import auth_service
from app.domain.entities import Usuario
from app.presentation.dependencies import get_current_user, get_db
from app.presentation.schemas.dtos import (
    ErrorOut,
    LoginRequest,
    LogoutRequest,
    MensajeOut,
    RecuperacionRespuesta,
    RecuperacionRestablecer,
    RecuperacionSolicitud,
    RefreshRequest,
    RegistroRequest,
    TokenPair,
    UsuarioOut,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])

ERR_422 = {"model": ErrorOut, "description": "Datos inválidos"}
ERR_401 = {"model": ErrorOut, "description": "Credenciales o token inválidos"}
ERR_403 = {"model": ErrorOut, "description": "Cuenta bloqueada, inactiva o sin permisos"}


@router.post(
    "/registro",
    response_model=UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una cuenta",
    description="Crea una cuenta con rol estudiante. La contraseña debe tener al "
    "menos 12 caracteres, mayúscula, minúscula, dígito y símbolo.",
    responses={
        400: {"model": ErrorOut, "description": "Contraseña débil"},
        409: {"model": ErrorOut, "description": "Correo ya registrado"},
        422: ERR_422,
    },
)
def registro(data: RegistroRequest, db: Session = Depends(get_db)):
    return auth_service.registrar(db, data)


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Iniciar sesión",
    description="Devuelve un token de acceso JWT (15 min) y un refresh token opaco. "
    "Tras 5 intentos fallidos la cuenta se bloquea 15 minutos.",
    responses={401: ERR_401, 403: ERR_403, 422: ERR_422},
)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, data.correo, data.password)


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Renovar el token de acceso",
    description="Rota el refresh token: el token enviado queda revocado y se emite "
    "uno nuevo. Reutilizar un token revocado cierra todas las sesiones.",
    responses={401: ERR_401, 403: ERR_403, 422: ERR_422},
)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return auth_service.refrescar(db, data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar sesión",
    description="Revoca el refresh token indicado. La operación es idempotente.",
    responses={422: ERR_422},
)
def logout(data: LogoutRequest, db: Session = Depends(get_db)):
    auth_service.logout(db, data.refresh_token)


@router.get(
    "/me",
    response_model=UsuarioOut,
    summary="Perfil del usuario autenticado",
    description="Requiere `Authorization: Bearer <access_token>`.",
    responses={401: ERR_401, 403: ERR_403},
)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.post(
    "/recuperacion/solicitar",
    response_model=RecuperacionRespuesta,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Solicitar recuperación de contraseña",
    description="Genera un JWT de propósito exclusivo con `jti` de un solo uso. "
    "En desarrollo se envía a Mailpit y además se devuelve el enlace en el JSON.",
    responses={422: ERR_422},
)
def solicitar_recuperacion(data: RecuperacionSolicitud, db: Session = Depends(get_db)):
    return auth_service.solicitar_recuperacion(db, data.correo)


@router.post(
    "/recuperacion/restablecer",
    response_model=MensajeOut,
    summary="Restablecer la contraseña con el enlace",
    description="Valida el propósito del token, que el `jti` no se haya usado y que "
    "no esté expirado. Al restablecer se invalidan todas las sesiones previas.",
    responses={
        400: {"model": ErrorOut, "description": "Contraseña débil"},
        401: ERR_401,
        422: ERR_422,
    },
)
def restablecer_password(data: RecuperacionRestablecer, db: Session = Depends(get_db)):
    auth_service.restablecer_password(db, data.token, data.password_nueva)
    return {"mensaje": "Contraseña actualizada. Inicia sesión con la nueva contraseña."}
