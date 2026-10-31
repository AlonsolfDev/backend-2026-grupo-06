"""
Casos de uso de Equipamiento: lógica de negocio y coordinación con el repositorio.
"""
from app.domain.entities import Equipamiento, EstadoEquipamiento
from app.infrastructure.repositories.equipamiento_repository import equipamiento_store
from app.infrastructure.repositories.sala_repository import sala_store
from app.presentation.schemas.dtos import EquipamientoCreate


def crear_equipamiento(data: EquipamientoCreate) -> Equipamiento:
    if sala_store.get(data.sala_id) is None:
        raise ValueError(f"No existe una sala con ID {data.sala_id}.")
    return equipamiento_store.add(
        lambda nuevo_id: Equipamiento(
            id=nuevo_id,
            nombre=data.nombre,
            tipo=data.tipo,
            estado=EstadoEquipamiento.DISPONIBLE,
            sala_id=data.sala_id,
        )
    )


def listar_equipamientos() -> list[Equipamiento]:
    return equipamiento_store.list_all()


def obtener_equipamiento(equipamiento_id: int) -> Equipamiento:
    equipamiento = equipamiento_store.get(equipamiento_id)
    if equipamiento is None:
        raise ValueError(f"No existe un equipamiento con ID {equipamiento_id}.")
    return equipamiento


def actualizar_estado_equipamiento(equipamiento_id: int, nuevo_estado: EstadoEquipamiento) -> Equipamiento:
    equipamiento = obtener_equipamiento(equipamiento_id)
    equipamiento_actualizado = Equipamiento(
        id=equipamiento.id,
        nombre=equipamiento.nombre,
        tipo=equipamiento.tipo,
        estado=nuevo_estado,
        sala_id=equipamiento.sala_id,
    )
    equipamiento_store.update(equipamiento_id, equipamiento_actualizado)
    return equipamiento_actualizado