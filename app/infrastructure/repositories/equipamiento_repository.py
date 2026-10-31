from sqlalchemy.orm import Session

from app.domain.entities import Equipamiento
from app.infrastructure.mappers.equipamiento_mapper import (
    equipamiento_a_dominio,
    equipamiento_a_modelo,
)
from app.infrastructure.models import EquipamientoModel


class EquipamientoRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Equipamiento]:
        return [equipamiento_a_dominio(m) for m in self.db.query(EquipamientoModel).all()]

    def listar_por_sala(self, sala_id: int) -> list[Equipamiento]:
        modelos = self.db.query(EquipamientoModel).filter_by(sala_id=sala_id).all()
        return [equipamiento_a_dominio(m) for m in modelos]

    def obtener_por_id(self, equipamiento_id: int) -> Equipamiento | None:
        modelo = self.db.get(EquipamientoModel, equipamiento_id)
        return equipamiento_a_dominio(modelo) if modelo else None

    def crear(self, equipamiento: Equipamiento) -> Equipamiento:
        modelo = equipamiento_a_modelo(equipamiento)
        modelo.id = None  # la base de datos asigna el ID
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        return equipamiento_a_dominio(modelo)

    def actualizar(self, equipamiento: Equipamiento) -> Equipamiento:
        modelo = self.db.merge(equipamiento_a_modelo(equipamiento))
        self.db.commit()
        self.db.refresh(modelo)
        return equipamiento_a_dominio(modelo)

    def eliminar(self, equipamiento_id: int) -> bool:
        modelo = self.db.get(EquipamientoModel, equipamiento_id)
        if not modelo:
            return False
        self.db.delete(modelo)
        self.db.commit()
        return True