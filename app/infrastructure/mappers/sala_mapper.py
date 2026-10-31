from app.domain.entities import Sala
from app.infrastructure.models import SalaModel


def sala_a_dominio(modelo: SalaModel) -> Sala:
    return Sala(
        id=modelo.id,
        nombre=modelo.nombre,
        capacidad=modelo.capacidad,
        ubicacion=modelo.ubicacion,
        estado=modelo.estado,
    )


def sala_a_modelo(entidad: Sala) -> SalaModel:
    return SalaModel(
        id=entidad.id,
        nombre=entidad.nombre,
        capacidad=entidad.capacidad,
        ubicacion=entidad.ubicacion,
        estado=entidad.estado,
    )
