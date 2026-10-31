"""
Casos de uso de Reserva: lógica de negocio, validaciones y coordinación
con el repositorio.
"""
from app.domain.entities import Reserva, EstadoReserva
from app.domain.reglas_negocio import (
    validar_fechas_reserva,
    validar_disponibilidad_sala,
)
from app.infrastructure.repositories.reserva_repository import reserva_store
from app.infrastructure.repositories.sala_repository import sala_store
from app.infrastructure.repositories.usuario_repository import usuario_store
from app.presentation.schemas.dtos import ReservaCreate


def crear_reserva(data: ReservaCreate) -> Reserva:
    # Validación de existencia relacionada: usuario y sala deben existir
    if usuario_store.get(data.usuario_id) is None:
        raise ValueError(f"No existe un usuario con ID {data.usuario_id}.")
    if sala_store.get(data.sala_id) is None:
        raise ValueError(f"No existe una sala con ID {data.sala_id}.")

    # Regla de negocio 1: fecha_fin no puede ser <= fecha_inicio
    validar_fechas_reserva(data.fecha_inicio, data.fecha_fin)

    # Regla de negocio 2: no solapar con otra reserva confirmada en la misma sala
    reservas_existentes = reserva_store.list_all()
    validar_disponibilidad_sala(
        data.sala_id, data.fecha_inicio, data.fecha_fin, reservas_existentes
    )

    return reserva_store.add(
        lambda nuevo_id: Reserva(
            id=nuevo_id,
            usuario_id=data.usuario_id,
            sala_id=data.sala_id,
            fecha_inicio=data.fecha_inicio,
            fecha_fin=data.fecha_fin,
            estado=EstadoReserva.PENDIENTE,
        )
    )


def listar_reservas() -> list[Reserva]:
    return reserva_store.list_all()


def obtener_reserva(reserva_id: int) -> Reserva:
    reserva = reserva_store.get(reserva_id)
    if reserva is None:
        raise ValueError(f"No existe una reserva con ID {reserva_id}.")
    return reserva


def actualizar_reserva(reserva_id: int, data: ReservaCreate) -> Reserva:
    obtener_reserva(reserva_id)  # valida que exista

    if usuario_store.get(data.usuario_id) is None:
        raise ValueError(f"No existe un usuario con ID {data.usuario_id}.")
    if sala_store.get(data.sala_id) is None:
        raise ValueError(f"No existe una sala con ID {data.sala_id}.")

    validar_fechas_reserva(data.fecha_inicio, data.fecha_fin)

    reservas_existentes = [
        r for r in reserva_store.list_all() if r.id != reserva_id
    ]
    validar_disponibilidad_sala(
        data.sala_id, data.fecha_inicio, data.fecha_fin, reservas_existentes
    )

    reserva_actualizada = Reserva(
        id=reserva_id,
        usuario_id=data.usuario_id,
        sala_id=data.sala_id,
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
        estado=EstadoReserva.PENDIENTE,
    )
    reserva_store.update(reserva_id, reserva_actualizada)
    return reserva_actualizada


def confirmar_reserva(reserva_id: int) -> Reserva:
    reserva = obtener_reserva(reserva_id)
    reserva_confirmada = Reserva(
        id=reserva.id,
        usuario_id=reserva.usuario_id,
        sala_id=reserva.sala_id,
        fecha_inicio=reserva.fecha_inicio,
        fecha_fin=reserva.fecha_fin,
        estado=EstadoReserva.CONFIRMADA,
    )
    reserva_store.update(reserva_id, reserva_confirmada)
    return reserva_confirmada


def eliminar_reserva(reserva_id: int) -> None:
    obtener_reserva(reserva_id)
    reserva_store.delete(reserva_id)