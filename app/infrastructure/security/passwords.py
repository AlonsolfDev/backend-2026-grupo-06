"""
Hash y verificación de contraseñas con Argon2id.

Se usa Argon2id (no SHA-256 ni MD5) porque es el algoritmo recomendado por
OWASP para almacenar contraseñas: es resistente a fuerza bruta por GPU y
permite ajustar tiempo, memoria y paralelismo.
"""

import re

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from app.infrastructure.config import PASSWORD_MIN_LARGO

# Parámetros de Argon2id: ~64 MB de memoria y 3 iteraciones.
_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16,
)


def hash_password(password: str) -> str:
    """Devuelve el hash Argon2id de la contraseña (incluye sal aleatoria)."""
    return _hasher.hash(password)


def verificar_password(password: str, password_hash: str) -> bool:
    """Compara una contraseña en claro con su hash. Nunca lanza excepción."""
    if not password_hash:
        return False
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def necesita_rehash(password_hash: str) -> bool:
    """Indica si el hash fue creado con parámetros distintos a los actuales."""
    try:
        return _hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return False


def errores_de_password(password: str) -> list[str]:
    """Devuelve la lista de requisitos incumplidos (vacía si es válida)."""
    errores: list[str] = []
    if len(password) < PASSWORD_MIN_LARGO:
        errores.append(f"Debe tener al menos {PASSWORD_MIN_LARGO} caracteres.")
    if not re.search(r"[A-Z]", password):
        errores.append("Debe incluir al menos una letra mayúscula.")
    if not re.search(r"[a-z]", password):
        errores.append("Debe incluir al menos una letra minúscula.")
    if not re.search(r"\d", password):
        errores.append("Debe incluir al menos un dígito.")
    if not re.search(r"[^A-Za-z0-9]", password):
        errores.append("Debe incluir al menos un símbolo.")
    return errores
