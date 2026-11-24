from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities import RolUsuario
from app.infrastructure.database import Base


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    correo: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    rol: Mapped[RolUsuario] = mapped_column(Enum(RolUsuario, native_enum=False))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Credenciales. Argon2id produce hashes largos; 255 caracteres es holgado.
    password_hash: Mapped[str] = mapped_column(String(255), default="")
    intentos_fallidos: Mapped[int] = mapped_column(Integer, default=0)
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    reservas: Mapped[list["ReservaModel"]] = relationship(back_populates="usuario")
    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
