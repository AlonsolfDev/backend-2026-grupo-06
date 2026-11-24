"""
Excepciones propias del dominio. Cada una representa un tipo de error
que la capa de presentación convierte en un código HTTP distinto.

Heredan de ValueError para que exista un único respaldo: si alguna se
escapa, el manejador genérico la convierte en una respuesta controlada.
"""


class RecursoNoEncontrado(ValueError):
    """El recurso solicitado no existe (HTTP 404)."""


class ConflictoError(ValueError):
    """La operación choca con el estado actual, por ejemplo un solapamiento (HTTP 409)."""


class ReglaNegocioError(ValueError):
    """Se viola una regla de negocio del dominio (HTTP 400)."""


class NoAutenticado(ValueError):
    """Falta el token o es inválido/expirado (HTTP 401)."""


class TokenInvalido(NoAutenticado):
    """El token no corresponde al propósito esperado o ya fue usado (HTTP 401)."""


class Prohibido(ValueError):
    """El usuario está autenticado pero no tiene permiso para la acción (HTTP 403)."""


class CuentaBloqueada(ValueError):
    """La cuenta está bloqueada temporalmente por intentos fallidos (HTTP 403)."""
