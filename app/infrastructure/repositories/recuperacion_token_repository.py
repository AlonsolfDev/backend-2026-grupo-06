from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.entities import RecuperacionToken
from app.infrastructure.models import RecuperacionTokenModel


def _a_dominio(modelo: RecuperacionTokenModel) -> RecuperacionToken:
    return RecuperacionToken(
        id=modelo.id,
        usuario_id=modelo.usuario_id,
        jti=modelo.jti,
        expira_en=modelo.expira_en,
        usado=modelo.usado,
        creado_en=modelo.creado_en,
    )


class RecuperacionTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, usuario_id: int, jti: str, expira_en: datetime) -> RecuperacionToken:
        modelo = RecuperacionTokenModel(
            usuario_id=usuario_id, jti=jti, expira_en=expira_en, usado=False
        )
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        return _a_dominio(modelo)

    def obtener_por_jti(self, jti: str) -> RecuperacionToken | None:
        modelo = (
            self.db.query(RecuperacionTokenModel).filter(RecuperacionTokenModel.jti == jti).first()
        )
        return _a_dominio(modelo) if modelo else None

    def obtener_ultimo_por_usuario(self, usuario_id: int) -> RecuperacionToken | None:
        """Devuelve la solicitud más reciente, usada o pendiente, de una cuenta."""
        modelo = (
            self.db.query(RecuperacionTokenModel)
            .filter(RecuperacionTokenModel.usuario_id == usuario_id)
            .order_by(
                RecuperacionTokenModel.creado_en.desc(),
                RecuperacionTokenModel.id.desc(),
            )
            .first()
        )
        return _a_dominio(modelo) if modelo else None

    def marcar_usado(self, jti: str) -> bool:
        modelo = (
            self.db.query(RecuperacionTokenModel)
            .filter(RecuperacionTokenModel.jti == jti, RecuperacionTokenModel.usado.is_(False))
            .first()
        )
        if modelo is None:
            return False
        modelo.usado = True
        self.db.commit()
        return True

    def invalidar_pendientes(self, usuario_id: int) -> int:
        """Invalida los enlaces de recuperación que aún no se usaron."""
        cantidad = (
            self.db.query(RecuperacionTokenModel)
            .filter(
                RecuperacionTokenModel.usuario_id == usuario_id,
                RecuperacionTokenModel.usado.is_(False),
            )
            .update({RecuperacionTokenModel.usado: True})
        )
        self.db.commit()
        return cantidad
