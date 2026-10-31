from app.domain.entities import Reserva
from app.infrastructure.models import ReservaModel


def reserva_a_dominio(modelo: ReservaModel) -> Reserva:
    return Reserva(
        id=modelo.id,
        usuario_id=modelo.usuario_id,
        sala_id=modelo.sala_id,
        fecha_inicio=modelo.fecha_inicio,
        fecha_fin=modelo.fecha_fin,
        proposito=modelo.proposito,
        num_asistentes=modelo.num_asistentes,
        estado=modelo.estado,
    )


def reserva_a_modelo(entidad: Reserva) -> ReservaModel:
    return ReservaModel(
        id=entidad.id,
        usuario_id=entidad.usuario_id,
        sala_id=entidad.sala_id,
        fecha_inicio=entidad.fecha_inicio,
        fecha_fin=entidad.fecha_fin,
        proposito=entidad.proposito,
        num_asistentes=entidad.num_asistentes,
        estado=entidad.estado,
    )
