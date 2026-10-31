from sqlalchemy.orm import Session

from app.domain.entities import Reserva
from app.infrastructure.mappers.reserva_mapper import reserva_a_dominio, reserva_a_modelo
from app.infrastructure.models import ReservaModel


class ReservaRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Reserva]:
        return [reserva_a_dominio(m) for m in self.db.query(ReservaModel).all()]

    def listar_por_sala(self, sala_id: int) -> list[Reserva]:
        modelos = self.db.query(ReservaModel).filter_by(sala_id=sala_id).all()
        return [reserva_a_dominio(m) for m in modelos]

    def obtener_por_id(self, reserva_id: int) -> Reserva | None:
        modelo = self.db.get(ReservaModel, reserva_id)
        return reserva_a_dominio(modelo) if modelo else None

    def crear(self, reserva: Reserva) -> Reserva:
        modelo = reserva_a_modelo(reserva)
        modelo.id = None  # la base de datos asigna el ID
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        return reserva_a_dominio(modelo)

    def actualizar(self, reserva: Reserva) -> Reserva:
        modelo = self.db.merge(reserva_a_modelo(reserva))
        self.db.commit()
        self.db.refresh(modelo)
        return reserva_a_dominio(modelo)

    def eliminar(self, reserva_id: int) -> bool:
        modelo = self.db.get(ReservaModel, reserva_id)
        if not modelo:
            return False
        self.db.delete(modelo)
        self.db.commit()
        return True