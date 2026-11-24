"""
Reglas de negocio del dominio de reservas.

Importante: una regla de negocio expresa una decisión o restricción del
dominio (ej. "una reserva no puede finalizar antes de comenzar"), no una
validación de tipo o formato (ej. "el nombre es texto").

Las reglas son funciones puras: reciben datos del dominio y lanzan una
excepción de dominio. No conocen FastAPI ni SQLAlchemy, por lo que pueden
probarse de forma unitaria sin base de datos.
"""

from collections.abc import Iterable
from datetime import datetime

from .entities import (
    Equipamiento,
    EstadoEquipamiento,
    EstadoReserva,
    EstadoSala,
    Reserva,
    Sala,
)
from .errores import ConflictoError, ReglaNegocioError


def validar_fechas_reserva(fecha_inicio: datetime, fecha_fin: datetime) -> None:
    """Regla de negocio 1: una reserva no puede finalizar antes de comenzar."""
    if fecha_fin <= fecha_inicio:
        raise ReglaNegocioError("La fecha de término no puede ser anterior o igual a la de inicio.")


def validar_disponibilidad_sala(
    sala_id: int,
    fecha_inicio: datetime,
    fecha_fin: datetime,
    reservas_existentes: Iterable[Reserva],
) -> None:
    """Regla de negocio 2: no se puede reservar una sala que ya tiene otra
    reserva confirmada que se solape en el mismo horario."""
    for reserva in reservas_existentes:
        if reserva.sala_id != sala_id:
            continue
        if reserva.estado != EstadoReserva.CONFIRMADA:
            continue
        se_solapan = fecha_inicio < reserva.fecha_fin and fecha_fin > reserva.fecha_inicio
        if se_solapan:
            raise ConflictoError("La sala ya tiene una reserva confirmada en ese horario.")


def validar_equipamiento_disponible(equipos: Iterable[Equipamiento]) -> None:
    """Regla de negocio 3: no se puede asociar equipamiento dañado a una reserva.

    Se invoca al confirmar una reserva: si la sala tiene equipamiento dañado,
    la reserva no puede quedar confirmada hasta que el equipo sea reparado.
    """
    for equipo in equipos:
        if equipo.estado == EstadoEquipamiento.DANADO:
            raise ReglaNegocioError(
                f"El equipamiento '{equipo.nombre}' está dañado y no puede reservarse."
            )


def validar_capacidad_sala(sala: Sala, num_asistentes: int) -> None:
    """Regla de negocio 4: los asistentes no pueden superar la capacidad."""
    if num_asistentes > sala.capacidad:
        raise ReglaNegocioError(
            f"La sala '{sala.nombre}' tiene capacidad para {sala.capacidad} personas "
            f"y se intentaron registrar {num_asistentes} asistentes."
        )


def validar_sala_operativa(sala: Sala) -> None:
    """Regla de negocio 5: no se reserva una sala en mantenimiento."""
    if sala.estado == EstadoSala.MANTENIMIENTO:
        raise ConflictoError(
            f"La sala '{sala.nombre}' está en mantenimiento y no puede reservarse."
        )
