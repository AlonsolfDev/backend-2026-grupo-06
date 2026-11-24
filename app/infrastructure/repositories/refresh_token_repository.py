from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.domain.entities import RefreshToken
from app.infrastructure.models import RefreshTokenModel


def _a_dominio(modelo: RefreshTokenModel) -> RefreshToken:
    return RefreshToken(
        id=modelo.id,
        usuario_id=modelo.usuario_id,
        token_hash=modelo.token_hash,
        expira_en=modelo.expira_en,
        revocado=modelo.revocado,
        creado_en=modelo.creado_en,
    )


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, usuario_id: int, token_hash: str, expira_en: datetime) -> RefreshToken:
        modelo = RefreshTokenModel(
            usuario_id=usuario_id,
            token_hash=token_hash,
            expira_en=expira_en,
            revocado=False,
            creado_en=datetime.now(UTC).replace(tzinfo=None),
        )
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        return _a_dominio(modelo)

    def obtener_por_hash(self, token_hash: str) -> RefreshToken | None:
        modelo = (
            self.db.query(RefreshTokenModel)
            .filter(RefreshTokenModel.token_hash == token_hash)
            .first()
        )
        return _a_dominio(modelo) if modelo else None

    def revocar(self, token_hash: str) -> bool:
        modelo = (
            self.db.query(RefreshTokenModel)
            .filter(RefreshTokenModel.token_hash == token_hash)
            .first()
        )
        if modelo is None:
            return False
        modelo.revocado = True
        self.db.commit()
        return True

    def revocar_todos_de_usuario(self, usuario_id: int) -> int:
        """Invalida todas las sesiones del usuario (logout global y recuperación)."""
        cantidad = (
            self.db.query(RefreshTokenModel)
            .filter(
                RefreshTokenModel.usuario_id == usuario_id,
                RefreshTokenModel.revocado.is_(False),
            )
            .update({RefreshTokenModel.revocado: True})
        )
        self.db.commit()
        return cantidad
