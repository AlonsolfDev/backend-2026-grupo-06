"""
Excepciones propias del dominio. Cada una representa un tipo de error
que la capa de presentación convierte en un código HTTP distinto.
Heredan de ValueError para no dejar escapar errores sin controlar.
"""


class RecursoNoEncontrado(ValueError):
    """El recurso solicitado no existe (HTTP 404)."""


class ConflictoError(ValueError):
    """La operación choca con el estado actual, por ejemplo un solapamiento (HTTP 409)."""


class ReglaNegocioError(ValueError):
    """Se viola una regla de negocio del dominio (HTTP 400)."""