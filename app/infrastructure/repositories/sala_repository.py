from sqlalchemy.orm import Session

from app.domain.entities import Sala
from app.infrastructure.mappers.sala_mapper import sala_a_dominio, sala_a_modelo
from app.infrastructure.models import SalaModel


class SalaRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Sala]:
        return [sala_a_dominio(m) for m in self.db.query(SalaModel).all()]

    def obtener_por_id(self, sala_id: int) -> Sala | None:
        modelo = self.db.get(SalaModel, sala_id)
        return sala_a_dominio(modelo) if modelo else None

    def crear(self, sala: Sala) -> Sala:
        modelo = sala_a_modelo(sala)
        modelo.id = None  # la base de datos asigna el ID
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        return sala_a_dominio(modelo)

    def actualizar(self, sala: Sala) -> Sala:
        modelo = self.db.merge(sala_a_modelo(sala))
        self.db.commit()
        self.db.refresh(modelo)
        return sala_a_dominio(modelo)

    def eliminar(self, sala_id: int) -> bool:
        modelo = self.db.get(SalaModel, sala_id)
        if not modelo:
            return False
        self.db.delete(modelo)
        self.db.commit()
        return True