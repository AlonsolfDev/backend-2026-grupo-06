"""
Envío del correo de recuperación.

En desarrollo se apunta a **Mailpit** (contenedor incluido en `compose.yaml`):
la API entrega el correo por SMTP en `mailpit:1025` y el buzón se revisa en
`http://localhost:8025`. Si no hay SMTP configurado, el envío se omite y la
solicitud sigue funcionando (el enlace se devuelve en el JSON en modo dev).
"""

import logging
import smtplib
from email.message import EmailMessage

from app.infrastructure.config import (
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_REMITENTE,
    SMTP_USUARIO,
)

logger = logging.getLogger(__name__)


def enviar_correo_recuperacion(destinatario: str, enlace: str) -> bool:
    """Intenta enviar el correo. Devuelve True si se entregó al servidor SMTP."""
    if not SMTP_HOST:
        logger.info("SMTP no configurado: se omite el envío del correo de recuperación.")
        return False

    mensaje = EmailMessage()
    mensaje["Subject"] = "Recuperación de contraseña - Reservas UCT"
    mensaje["From"] = SMTP_REMITENTE
    mensaje["To"] = destinatario
    mensaje.set_content(
        "Recibimos una solicitud para restablecer tu contraseña.\n\n"
        f"Abre este enlace para continuar: {enlace}\n\n"
        "El enlace caduca en 15 minutos y solo puede usarse una vez. "
        "Si no solicitaste el cambio, ignora este mensaje."
    )

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=5) as smtp:
            if SMTP_USUARIO:
                smtp.login(SMTP_USUARIO, SMTP_PASSWORD)
            smtp.send_message(mensaje)
        return True
    except OSError:
        # Un fallo de correo no debe tumbar la solicitud de recuperación.
        logger.exception("No se pudo enviar el correo de recuperación vía SMTP.")
        return False
