"""
Configuración central leída desde variables de entorno.

Todos los valores tienen un valor por defecto seguro para desarrollo local;
en producción se sobreescriben con el archivo `.env` (ver `.env.example`).
"""

import os

# --- Seguridad de tokens -------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "clave-de-desarrollo-grupo06-cambiar-en-produccion")
ALGORITHM = "HS256"

ACCESS_TOKEN_MINUTOS = int(os.getenv("ACCESS_TOKEN_MINUTOS", "15"))
REFRESH_TOKEN_DIAS = int(os.getenv("REFRESH_TOKEN_DIAS", "7"))
RECUPERACION_MINUTOS = int(os.getenv("RECUPERACION_MINUTOS", "15"))

# --- Política de contraseñas y bloqueo -----------------------------------
PASSWORD_MIN_LARGO = int(os.getenv("PASSWORD_MIN_LARGO", "12"))
MAX_INTENTOS_FALLIDOS = int(os.getenv("MAX_INTENTOS_FALLIDOS", "5"))
BLOQUEO_MINUTOS = int(os.getenv("BLOQUEO_MINUTOS", "15"))

# --- Entorno -------------------------------------------------------------
ENTORNO = os.getenv("ENTORNO", "dev").lower()

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
