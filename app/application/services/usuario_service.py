"""
Casos de uso de Usuario: lógica de negocio y coordinación con el repositorio.
"""
from app.domain.entities import Usuario
from app.infrastructure.repositories.usuario_repository import usuario_store
from app.presentation.schemas.dtos import UsuarioCreate


def crear_usuario(data: UsuarioCreate) -> Usuario:
    return usuario_store.add(
        lambda nuevo_id: Usuario(
            id=nuevo_id,
            nombre=data.nombre,
            correo=data.correo,
            rol=data.rol,
            activo=True,
        )
    )


def listar_usuarios() -> list[Usuario]:
    return usuario_store.list_all()


def obtener_usuario(usuario_id: int) -> Usuario:
    usuario = usuario_store.get(usuario_id)
    if usuario is None:
        raise ValueError(f"No existe un usuario con ID {usuario_id}.")
    return usuario