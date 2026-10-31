from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities import EstadoSala
from app.infrastructure.database import Base


class SalaModel(Base):
    __tablename__ = "salas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    capacidad: Mapped[int] = mapped_column(Integer)
    ubicacion: Mapped[str] = mapped_column(String(120))
    estado: Mapped[EstadoSala] = mapped_column(Enum(EstadoSala, native_enum=False))

    equipamientos: Mapped[list["EquipamientoModel"]] = relationship(back_populates="sala")
    reservas: Mapped[list["ReservaModel"]] = relationship(back_populates="sala")