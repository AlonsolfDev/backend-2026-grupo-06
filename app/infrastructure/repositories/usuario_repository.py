from sqlalchemy.orm import Session

from app.domain.entities import Usuario
from app.infrastructure.mappers.usuario_mapper import usuario_a_dominio, usuario_a_modelo
from app.infrastructure.models import UsuarioModel


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self) -> list[Usuario]:
        return [usuario_a_dominio(m) for m in self.db.query(UsuarioModel).all()]

    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        modelo = self.db.get(UsuarioModel, usuario_id)
        return usuario_a_dominio(modelo) if modelo else None

    def crear(self, usuario: Usuario) -> Usuario:
        modelo = usuario_a_modelo(usuario)
        modelo.id = None  # la base de datos asigna el ID
        self.db.add(modelo)
        self.db.commit()
        self.db.refresh(modelo)
        return usuario_a_dominio(modelo)

    def actualizar(self, usuario: Usuario) -> Usuario:
        modelo = self.db.merge(usuario_a_modelo(usuario))
        self.db.commit()
        self.db.refresh(modelo)
        return usuario_a_dominio(modelo)

    def eliminar(self, usuario_id: int) -> bool:
        modelo = self.db.get(UsuarioModel, usuario_id)
        if not modelo:
            return False
        self.db.delete(modelo)
        self.db.commit()
        return True