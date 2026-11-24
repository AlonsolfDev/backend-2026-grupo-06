"""
Dependencias por solicitud: sesión de BD y usuario autenticado.

El esquema es `Authorization: Bearer <access_token>`. Los errores de
autenticación se lanzan como excepciones de dominio para que `main.py` los
traduzca al formato uniforme de error (401 frente a 403).
"""

from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.services import auth_service
from app.domain.entities import RolUsuario, Usuario
from app.domain.errores import NoAutenticado, Prohibido
from app.infrastructure.database import SessionLocal

_bearer = HTTPBearer(auto_error=False, description="Token JWT de acceso")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    """401 si falta el token o es inválido/expirado."""
    if credenciales is None or not credenciales.credentials:
        raise NoAutenticado("Falta el token de acceso (Authorization: Bearer ...).")
    return auth_service.usuario_desde_token(db, credenciales.credentials)


def require_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    """403 si el usuario está autenticado pero no es administrador."""
    if usuario.rol != RolUsuario.ADMINISTRADOR:
        raise Prohibido("Esta operación requiere el rol administrador.")
    return usuario
