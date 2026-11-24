"""
Emisión y validación de tokens.

Dos tipos de token conviven, cada uno con un propósito exclusivo:

1. `acceso`      -> JWT firmado (HS256), vida corta (15 min por defecto).
2. `recuperacion` -> JWT firmado con un `jti` registrado en la base, de un
                    solo uso e independiente de los tokens de acceso.

El token de refresco es **opaco** (no es un JWT): es una cadena aleatoria de
256 bits. En la base de datos solo se guarda su hash SHA-256, de modo que un
robo de la base no permite reutilizar las sesiones.
"""

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.domain.entities import PropositoToken, Usuario
from app.domain.errores import TokenInvalido
from app.infrastructure.config import (
    ACCESS_TOKEN_MINUTOS,
    ALGORITHM,
    RECUPERACION_MINUTOS,
    REFRESH_TOKEN_DIAS,
    SECRET_KEY,
)


def _ahora() -> datetime:
    return datetime.now(UTC)


def generar_jti() -> str:
    return uuid.uuid4().hex


def crear_token_acceso(usuario: Usuario) -> str:
    ahora = _ahora()
    payload = {
        "sub": str(usuario.id),
        "rol": usuario.rol.value,
        "tipo": PropositoToken.ACCESO.value,
        "jti": generar_jti(),
        "iat": ahora,
        "exp": ahora + timedelta(minutes=ACCESS_TOKEN_MINUTOS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def crear_token_recuperacion(usuario: Usuario) -> tuple[str, str, datetime]:
    """Devuelve (token, jti, expira_en) del JWT de recuperación."""
    ahora = _ahora()
    jti = generar_jti()
    expira = ahora + timedelta(minutes=RECUPERACION_MINUTOS)
    payload = {
        "sub": str(usuario.id),
        "tipo": PropositoToken.RECUPERACION.value,
        "jti": jti,
        "iat": ahora,
        "exp": expira,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, expira.replace(tzinfo=None)


def decodificar_token(token: str, proposito: PropositoToken) -> dict:
    """Valida firma, expiración y propósito. Lanza TokenInvalido si falla."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp", "iat", "sub", "jti"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenInvalido("El token expiró. Solicita uno nuevo.") from exc
    except jwt.PyJWTError as exc:
        raise TokenInvalido("El token es inválido.") from exc

    if payload.get("tipo") != proposito.value:
        raise TokenInvalido("El token no corresponde a este propósito.")
    return payload


def generar_refresh_token() -> tuple[str, str]:
    """Devuelve (token en claro para el cliente, hash SHA-256 para la base)."""
    token = secrets.token_urlsafe(48)
    return token, hash_refresh_token(token)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def expiracion_refresh() -> datetime:
    """Fecha de expiración del refresh token en hora UTC sin zona."""
    return (_ahora() + timedelta(days=REFRESH_TOKEN_DIAS)).replace(tzinfo=None)
