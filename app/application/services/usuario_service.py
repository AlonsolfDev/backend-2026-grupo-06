"""
Casos de uso de Usuario: lógica de negocio y coordinación con el repositorio.
"""
from sqlalchemy.orm import Session

from app.domain.entities import Usuario
from app.domain.errores import ConflictoError, RecursoNoEncontrado
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.presentation.schemas.dtos import UsuarioCreate


def crear_usuario(db: Session, data: UsuarioCreate) -> Usuario:
    repo = UsuarioRepository(db)
    # Regla de negocio: el correo debe ser único
    if any(u.correo.lower() == data.correo.lower() for u in repo.listar()):
        raise ConflictoError(f"Ya existe un usuario con el correo {data.correo}.")

    nuevo = Usuario(
        id=0,  # el repositorio asigna el ID real
        nombre=data.nombre,
        correo=data.correo,
        rol=data.rol,
        activo=True,
    )
    return repo.crear(nuevo)


def listar_usuarios(db: Session) -> list[Usuario]:
    return UsuarioRepository(db).listar()


def obtener_usuario(db: Session, usuario_id: int) -> Usuario:
    usuario = UsuarioRepository(db).obtener_por_id(usuario_id)
    if usuario is None:
        raise RecursoNoEncontrado(f"No existe un usuario con ID {usuario_id}.")
    return usuario