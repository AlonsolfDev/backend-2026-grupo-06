from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities import RolUsuario
from app.infrastructure.database import Base


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    correo: Mapped[str] = mapped_column(String(120), unique=True)
    rol: Mapped[RolUsuario] = mapped_column(Enum(RolUsuario, native_enum=False))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    reservas: Mapped[list["ReservaModel"]] = relationship(back_populates="usuario")