from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities import EstadoEquipamiento
from app.infrastructure.database import Base


class EquipamientoModel(Base):
    __tablename__ = "equipamientos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    tipo: Mapped[str] = mapped_column(String(50))
    estado: Mapped[EstadoEquipamiento] = mapped_column(
        Enum(EstadoEquipamiento, native_enum=False)
    )
    descripcion: Mapped[str] = mapped_column(String(200), default="")
    sala_id: Mapped[int] = mapped_column(ForeignKey("salas.id"))

    sala: Mapped["SalaModel"] = relationship(back_populates="equipamientos")
