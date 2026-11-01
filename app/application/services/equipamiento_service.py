"""
Casos de uso de Equipamiento: lógica de negocio y coordinación con el repositorio.
"""
from dataclasses import replace

from sqlalchemy.orm import Session

from app.domain.entities import Equipamiento, EstadoEquipamiento
from app.domain.errores import RecursoNoEncontrado
from app.infrastructure.repositories.equipamiento_repository import EquipamientoRepository
from app.infrastructure.repositories.sala_repository import SalaRepository
from app.presentation.schemas.dtos import EquipamientoCreate


def crear_equipamiento(db: Session, data: EquipamientoCreate) -> Equipamiento:
    # Validación de existencia relacionada: la sala debe existir
    if SalaRepository(db).obtener_por_id(data.sala_id) is None:
        raise RecursoNoEncontrado(f"No existe una sala con ID {data.sala_id}.")

    nuevo = Equipamiento(
        id=0,  # el repositorio asigna el ID real
        nombre=data.nombre,
        tipo=data.tipo,
        estado=EstadoEquipamiento.DISPONIBLE,
        sala_id=data.sala_id,
        descripcion=data.descripcion,
    )
    return EquipamientoRepository(db).crear(nuevo)


def listar_equipamientos(db: Session) -> list[Equipamiento]:
    return EquipamientoRepository(db).listar()


def obtener_equipamiento(db: Session, equipamiento_id: int) -> Equipamiento:
    equipamiento = EquipamientoRepository(db).obtener_por_id(equipamiento_id)
    if equipamiento is None:
        raise RecursoNoEncontrado(f"No existe un equipamiento con ID {equipamiento_id}.")
    return equipamiento


def actualizar_estado_equipamiento(
    db: Session, equipamiento_id: int, nuevo_estado: EstadoEquipamiento
) -> Equipamiento:
    equipamiento = obtener_equipamiento(db, equipamiento_id)
    actualizado = replace(equipamiento, estado=nuevo_estado)
    return EquipamientoRepository(db).actualizar(actualizado)