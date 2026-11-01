from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from app.domain.entities import EstadoSala, Sala
from app.infrastructure.mappers.sala_mapper import sala_a_dominio, sala_a_modelo
from app.infrastructure.models import SalaModel


class SalaRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Sala]:
        return [sala_a_dominio(m) for m in self.db.query(SalaModel).all()]

    def listar_paginado(
        self,
        estado: EstadoSala | None,
        ordenar_por: str,
        direccion: str,
        pagina: int,
        limite: int,
    ) -> tuple[list[Sala], int]:
        """Filtra, ordena y pagina en la base de datos. Devuelve (items, total)."""
        consulta = select(SalaModel)
        if estado is not None:
            consulta = consulta.where(SalaModel.estado == estado)

        # el total se calcula sobre los registros ya filtrados
        total = self.db.scalar(
            select(func.count()).select_from(consulta.subquery())
        ) or 0

        columna = getattr(SalaModel, ordenar_por)
        orden = desc(columna) if direccion == "desc" else asc(columna)
        consulta = consulta.order_by(orden).limit(limite).offset((pagina - 1) * limite)

        modelos = self.db.scalars(consulta).all()
        return [sala_a_dominio(m) for m in modelos], total

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