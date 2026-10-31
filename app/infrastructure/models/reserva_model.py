from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities import EstadoReserva
from app.infrastructure.database import Base


class ReservaModel(Base):
    __tablename__ = "reservas"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    sala_id: Mapped[int] = mapped_column(ForeignKey("salas.id"))
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime)
    fecha_fin: Mapped[datetime] = mapped_column(DateTime)
    proposito: Mapped[str] = mapped_column(String(200))
    num_asistentes: Mapped[int] = mapped_column(Integer)
    estado: Mapped[EstadoReserva] = mapped_column(
        Enum(EstadoReserva, native_enum=False), default=EstadoReserva.PENDIENTE
    )

    usuario: Mapped["UsuarioModel"] = relationship(back_populates="reservas")
    sala: Mapped["SalaModel"] = relationship(back_populates="reservas")
