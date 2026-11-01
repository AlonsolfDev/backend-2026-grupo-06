"""
Reglas de negocio del dominio de reservas.

Importante: una regla de negocio expresa una decisión o restricción del
dominio (ej. "una reserva no puede finalizar antes de comenzar"), no una
validación de tipo o formato (ej. "el nombre es texto").
"""
from datetime import datetime
from typing import Iterable

from .entities import Equipamiento, EstadoEquipamiento, EstadoReserva, Reserva
from .errores import ConflictoError, ReglaNegocioError


def validar_fechas_reserva(fecha_inicio: datetime, fecha_fin: datetime) -> None:
    """Regla de negocio 1: una reserva no puede finalizar antes de comenzar."""
    if fecha_fin <= fecha_inicio:
        raise ReglaNegocioError(
            "La fecha de término no puede ser anterior o igual a la de inicio."
        )


def validar_disponibilidad_sala(
    sala_id: int,
    fecha_inicio: datetime,
    fecha_fin: datetime,
    reservas_existentes: Iterable[Reserva],
) -> None:
    """Regla de negocio 2: no se puede reservar una sala que ya tiene otra
    reserva confirmada que se solape en el mismo horario."""
    # Las fechas del request llegan con zona horaria (UTC) y las de la BD no.
    fecha_inicio = fecha_inicio.replace(tzinfo=None)
    fecha_fin = fecha_fin.replace(tzinfo=None)

    for reserva in reservas_existentes:
        if reserva.sala_id != sala_id:
            continue
        if reserva.estado != EstadoReserva.CONFIRMADA:
            continue
        se_solapan = fecha_inicio < reserva.fecha_fin and fecha_fin > reserva.fecha_inicio
        if se_solapan:
            raise ConflictoError("La sala ya tiene una reserva confirmada en ese horario.")


def validar_equipamiento_disponible(equipos: Iterable[Equipamiento]) -> None:
    """Regla de negocio 3: no se puede asociar equipamiento dañado a una reserva."""
    for equipo in equipos:
        if equipo.estado == EstadoEquipamiento.DANADO:
            raise ReglaNegocioError(
                f"El equipamiento '{equipo.nombre}' está dañado y no puede reservarse."
            )