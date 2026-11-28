"""
Configuración central leída desde variables de entorno.

Todos los valores tienen un valor por defecto seguro para desarrollo local;
en producción se sobreescriben con el archivo `.env` (ver `.env.example`).
"""

import os

# --- Entorno -------------------------------------------------------------
ENTORNO = os.getenv("ENTORNO", "dev").lower()

# --- Seguridad de tokens -------------------------------------------------
_SECRET_KEY_POR_DEFECTO = "clave-de-desarrollo-grupo06-cambiar-en-produccion"
SECRET_KEY = (os.getenv("SECRET_KEY") or "").strip() or _SECRET_KEY_POR_DEFECTO
if ENTORNO == "produccion" and SECRET_KEY == _SECRET_KEY_POR_DEFECTO:
    raise RuntimeError("SECRET_KEY debe definirse con un valor propio cuando ENTORNO=produccion.")
ALGORITHM = "HS256"

ACCESS_TOKEN_MINUTOS = int(os.getenv("ACCESS_TOKEN_MINUTOS", "15"))
REFRESH_TOKEN_DIAS = int(os.getenv("REFRESH_TOKEN_DIAS", "7"))
RECUPERACION_MINUTOS = int(os.getenv("RECUPERACION_MINUTOS", "15"))

# Segundos mínimos entre solicitudes de recuperación de una misma cuenta.
# No bloquea la cuenta: solo evita que se generen y envíen enlaces en cadena.
RECUPERACION_COOLDOWN_SEGUNDOS = int(os.getenv("RECUPERACION_COOLDOWN_SEGUNDOS", "120"))

# --- Política de contraseñas y bloqueo -----------------------------------
PASSWORD_MIN_LARGO = int(os.getenv("PASSWORD_MIN_LARGO", "12"))
MAX_INTENTOS_FALLIDOS = int(os.getenv("MAX_INTENTOS_FALLIDOS", "5"))
BLOQUEO_MINUTOS = int(os.getenv("BLOQUEO_MINUTOS", "15"))

# --- CORS ----------------------------------------------------------------
# Lista explícita de orígenes autorizados, separados por coma. Nunca se usa
# "*" porque la API permite credenciales (cookies/refresh). En producción se
# debe definir CORS_ORIGINS con el dominio real del frontend.
_CORS_ORIGENES_POR_DEFECTO = (
    "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
)
CORS_ORIGINS = [
    origen.strip()
    for origen in os.getenv("CORS_ORIGINS", _CORS_ORIGENES_POR_DEFECTO).split(",")
    if origen.strip()
]
if "*" in CORS_ORIGINS:
    raise RuntimeError("CORS_ORIGINS debe enumerar orígenes explícitos; no se admite '*'.")

# --- Exposición del enlace de recuperación -------------------------------
# La pauta permite devolver el enlace de recuperación en la respuesta JSON
# en entornos de prueba. En producción se envía por correo y NO se expone.
EXPONER_ENLACE_RECUPERACION = os.getenv(
    "EXPONER_ENLACE_RECUPERACION", "true" if ENTORNO == "dev" else "false"
).lower() in ("1", "true", "yes", "si")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# --- Correo (Mailpit en desarrollo) --------------------------------------
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_USUARIO = os.getenv("SMTP_USUARIO", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_REMITENTE = os.getenv("SMTP_REMITENTE", "no-reply@reservas.uct.cl")
