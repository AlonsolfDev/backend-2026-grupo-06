from datetime import date, datetime, time

from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from app.domain.entities import EstadoReserva, Reserva
from app.infrastructure.mappers.reserva_mapper import reserva_a_dominio, reserva_a_modelo
from app.infrastructure.models import ReservaModel


class ReservaRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Reserva]:
        return [reserva_a_dominio(m) for m in self.db.query(ReservaModel).all()]

    def listar_paginado(
        self,
        usuario_id: int | None = None,
        sala_id: int | None = None,
        estado: EstadoReserva | None = None,
        fecha: date | None = None,
        ordenar_por: str = "fecha_inicio",
        direccion: str = "asc",
        pagina: int = 1,
        limite: int = 20,
    ) -> tuple[list[Reserva], int]:
        """Filtra, ordena y pagina en la base de datos. Devuelve (items, total).

        Los filtros son acumulativos: se pueden combinar usuario, sala, estado
        y fecha del día en una misma consulta.
        """
        consulta = select(ReservaModel)
        if usuario_id is not None:
            consulta = consulta.where(ReservaModel.usuario_id == usuario_id)
        if sala_id is not None:
            consulta = consulta.where(ReservaModel.sala_id == sala_id)
        if estado is not None:
            consulta = consulta.where(ReservaModel.estado == estado)
        if fecha is not None:
            inicio_dia = datetime.combine(fecha, time.min)
            fin_dia = datetime.combine(fecha, time.max)
            consulta = consulta.where(
                ReservaModel.fecha_inicio >= inicio_dia,
                ReservaModel.fecha_inicio <= fin_dia,
            )

        # el total se calcula sobre los registros ya filtrados
        total = self.db.scalar(select(func.count()).select_from(consulta.subquery())) or 0

        columna = getattr(ReservaModel, ordenar_por)
        orden = desc(columna) if direccion == "desc" else asc(columna)
        consulta = consulta.order_by(orden).limit(limite).offset((pagina - 1) * limite)

        modelos = self.db.scalars(consulta).all()
        return [reserva_a_dominio(m) for m in modelos], total

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
