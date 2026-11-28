"""
Casos de uso de autenticación: registro, login, refresh con rotación,
logout, recuperación de contraseña y autorización por rol.

Decisiones de seguridad (alineadas con la pauta):
- Contraseñas con Argon2id y mínimo 12 caracteres con complejidad.
- Token de acceso JWT de vida corta; token de refresco opaco guardado como hash.
- Rotación de refresh: cada uso revoca el anterior. Si se reutiliza un token
  ya revocado, se revocan TODAS las sesiones del usuario.
- Bloqueo temporal tras 5 intentos fallidos (401/403 diferenciados).
- Recuperación con JWT de propósito exclusivo (`recuperacion`), `jti` de un
  solo uso y revocación de todas las sesiones previas al restablecer.
"""

import logging
from dataclasses import replace
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.domain.entities import PropositoToken, RolUsuario, Usuario
from app.domain.errores import (
    CuentaBloqueada,
    NoAutenticado,
    Prohibido,
    ReglaNegocioError,
    TokenInvalido,
)
from app.infrastructure.config import (
    ACCESS_TOKEN_MINUTOS,
    BASE_URL,
    BLOQUEO_MINUTOS,
    EXPONER_ENLACE_RECUPERACION,
    MAX_INTENTOS_FALLIDOS,
    RECUPERACION_COOLDOWN_SEGUNDOS,
)
from app.infrastructure.repositories.recuperacion_token_repository import (
    RecuperacionTokenRepository,
)
from app.infrastructure.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.security.correo import enviar_correo_recuperacion
from app.infrastructure.security.passwords import (
    errores_de_password,
    hash_password,
    necesita_rehash,
    verificar_password,
)
from app.infrastructure.security.tokens import (
    crear_token_acceso,
    crear_token_recuperacion,
    decodificar_token,
    expiracion_refresh,
    generar_refresh_token,
    hash_refresh_token,
)
from app.presentation.schemas.dtos import RegistroRequest, UsuarioCreate

logger = logging.getLogger(__name__)

_MENSAJE_CREDENCIALES = "El correo o la contraseña no son correctos."


def _ahora_sin_zona() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _emitir_par_tokens(db: Session, usuario: Usuario) -> dict:
    refresh_claro, refresh_hash = generar_refresh_token()
    RefreshTokenRepository(db).crear(usuario.id, refresh_hash, expiracion_refresh())
    return {
        "access_token": crear_token_acceso(usuario),
        "refresh_token": refresh_claro,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_MINUTOS * 60,
    }


def registrar(db: Session, data: RegistroRequest) -> Usuario:
    """Registro público: siempre crea estudiantes (no permite escalar rol)."""
    from app.application.services import usuario_service

    return usuario_service.crear_usuario(
        db,
        UsuarioCreate(
            nombre=data.nombre,
            correo=data.correo,
            rol=RolUsuario.ESTUDIANTE,
            password=data.password,
        ),
    )


def login(db: Session, correo: str, password: str) -> dict:
    repo = UsuarioRepository(db)
    usuario = repo.obtener_por_correo(correo)
    if usuario is None:
        # Mismo mensaje que con contraseña incorrecta: no revela si el correo existe.
        raise NoAutenticado(_MENSAJE_CREDENCIALES)

    if not usuario.activo:
        raise Prohibido("La cuenta está desactivada. Contacta al administrador.")

    ahora = _ahora_sin_zona()
    if usuario.bloqueado_hasta and usuario.bloqueado_hasta > ahora:
        restantes = int((usuario.bloqueado_hasta - ahora).total_seconds() // 60) + 1
        raise CuentaBloqueada(
            f"La cuenta está bloqueada por intentos fallidos. "
            f"Intenta nuevamente en {restantes} minuto(s)."
        )

    if not verificar_password(password, usuario.password_hash):
        intentos = usuario.intentos_fallidos + 1
        if intentos >= MAX_INTENTOS_FALLIDOS:
            bloqueado = ahora + timedelta(minutes=BLOQUEO_MINUTOS)
            repo.actualizar(replace(usuario, intentos_fallidos=0, bloqueado_hasta=bloqueado))
            raise CuentaBloqueada(
                f"Demasiados intentos fallidos. La cuenta quedó bloqueada "
                f"{BLOQUEO_MINUTOS} minutos."
            )
        repo.actualizar(replace(usuario, intentos_fallidos=intentos))
        raise NoAutenticado(_MENSAJE_CREDENCIALES)

    # Login correcto: limpiar contadores y, si el hash quedó antiguo, actualizarlo.
    usuario_actualizado = replace(
        usuario,
        intentos_fallidos=0,
        bloqueado_hasta=None,
        password_hash=(
            hash_password(password)
            if necesita_rehash(usuario.password_hash)
            else usuario.password_hash
        ),
    )
    usuario_actualizado = repo.actualizar(usuario_actualizado)
    return _emitir_par_tokens(db, usuario_actualizado)


def refrescar(db: Session, refresh_claro: str) -> dict:
    """Rotación de refresh tokens con detección de reutilización."""
    repo = RefreshTokenRepository(db)
    hash_token = hash_refresh_token(refresh_claro)
    registro = repo.obtener_por_hash(hash_token)

    if registro is None:
        raise TokenInvalido("El token de refresco no es válido.")

    if registro.revocado:
        # Reutilización de un token ya rotado: se asume robo y se cierran
        # todas las sesiones del usuario.
        repo.revocar_todos_de_usuario(registro.usuario_id)
        logger.warning(
            "Reutilización de refresh token detectada para usuario %s", registro.usuario_id
        )
        raise TokenInvalido(
            "El token de refresco ya fue utilizado. Por seguridad se cerraron todas las sesiones."
        )

    if registro.expira_en < _ahora_sin_zona():
        repo.revocar(hash_token)
        raise TokenInvalido("El token de refresco expiró. Inicia sesión nuevamente.")

    usuario = UsuarioRepository(db).obtener_por_id(registro.usuario_id)
    if usuario is None or not usuario.activo:
        repo.revocar_todos_de_usuario(registro.usuario_id)
        raise Prohibido("La cuenta no está disponible.")

    repo.revocar(hash_token)  # rotación: el token usado deja de servir
    return _emitir_par_tokens(db, usuario)


def logout(db: Session, refresh_claro: str) -> None:
    """Revoca el refresh indicado. Es idempotente: no falla si ya no existe."""
    RefreshTokenRepository(db).revocar(hash_refresh_token(refresh_claro))


def solicitar_recuperacion(db: Session, correo: str) -> dict:
    usuario = UsuarioRepository(db).obtener_por_correo(correo)
    mensaje = (
        "Si el correo está registrado, recibirás un enlace de recuperación válido por 15 minutos."
    )

    # No se revela si el correo existe o no (evita enumeración de cuentas).
    if usuario is None or not usuario.activo:
        return {"mensaje": mensaje, "enlace_recuperacion": None}

    repo_tokens = RecuperacionTokenRepository(db)

    # Límite de solicitudes repetidas: dentro de la ventana se responde igual
    # (202 genérico) pero no se genera ni envía otro enlace. No se incrementan
    # intentos fallidos ni se bloquea la cuenta.
    ultimo = repo_tokens.obtener_ultimo_por_usuario(usuario.id)
    ahora = _ahora_sin_zona()
    if ultimo is not None and ultimo.creado_en is not None:
        transcurrido = (ahora - ultimo.creado_en).total_seconds()
        if transcurrido < RECUPERACION_COOLDOWN_SEGUNDOS:
            logger.info(
                "Solicitud de recuperación limitada para usuario %s (faltan %s s).",
                usuario.id,
                int(RECUPERACION_COOLDOWN_SEGUNDOS - transcurrido),
            )
            return {"mensaje": mensaje, "enlace_recuperacion": None}

    # Un nuevo enlace invalida los pendientes anteriores.
    repo_tokens.invalidar_pendientes(usuario.id)

    token, jti, expira = crear_token_recuperacion(usuario)
    repo_tokens.crear(usuario.id, jti, expira)

    enlace = f"{BASE_URL}/auth/recuperacion/restablecer?token={token}"
    enviar_correo_recuperacion(usuario.correo, enlace)

    return {
        "mensaje": mensaje,
        "enlace_recuperacion": enlace if EXPONER_ENLACE_RECUPERACION else None,
    }


def restablecer_password(db: Session, token: str, password_nueva: str) -> None:
    payload = decodificar_token(token, PropositoToken.RECUPERACION)
    jti = payload["jti"]
    usuario_id = int(payload["sub"])

    repo_tokens = RecuperacionTokenRepository(db)
    registro = repo_tokens.obtener_por_jti(jti)
    if registro is None:
        raise TokenInvalido("El enlace de recuperación no es válido.")
    if registro.usado:
        raise TokenInvalido("El enlace de recuperación ya fue utilizado.")
    if registro.expira_en < _ahora_sin_zona():
        raise TokenInvalido("El enlace de recuperación expiró.")

    errores = errores_de_password(password_nueva)
    if errores:
        raise ReglaNegocioError(
            "La contraseña no cumple la política de seguridad: " + " ".join(errores)
        )

    usuario = UsuarioRepository(db).obtener_por_id(usuario_id)
    if usuario is None:
        raise TokenInvalido("El enlace de recuperación no es válido.")

    # Uso único: el jti se marca antes de aplicar el cambio.
    repo_tokens.marcar_usado(jti)

    UsuarioRepository(db).actualizar(
        replace(
            usuario,
            password_hash=hash_password(password_nueva),
            intentos_fallidos=0,
            bloqueado_hasta=None,
        )
    )

    # Invalidación de sesiones previas: cualquier refresh emitido antes deja
    # de funcionar, y los enlaces de recuperación pendientes también.
    RefreshTokenRepository(db).revocar_todos_de_usuario(usuario.id)
    repo_tokens.invalidar_pendientes(usuario.id)


def usuario_desde_token(db: Session, token: str) -> Usuario:
    """Valida un token de acceso y devuelve el usuario autenticado."""
    payload = decodificar_token(token, PropositoToken.ACCESO)
    usuario = UsuarioRepository(db).obtener_por_id(int(payload["sub"]))
    if usuario is None:
        raise TokenInvalido("El usuario del token ya no existe.")
    if not usuario.activo:
        raise Prohibido("La cuenta está desactivada.")
    return usuario
