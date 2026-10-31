from app.domain.entities import Equipamiento
from app.infrastructure.models import EquipamientoModel


def equipamiento_a_dominio(modelo: EquipamientoModel) -> Equipamiento:
    return Equipamiento(
        id=modelo.id,
        nombre=modelo.nombre,
        tipo=modelo.tipo,
        estado=modelo.estado,
        sala_id=modelo.sala_id,
        descripcion=modelo.descripcion,
    )


def equipamiento_a_modelo(entidad: Equipamiento) -> EquipamientoModel:
    return EquipamientoModel(
        id=entidad.id,
        nombre=entidad.nombre,
        tipo=entidad.tipo,
        estado=entidad.estado,
        sala_id=entidad.sala_id,
        descripcion=entidad.descripcion,
    )
