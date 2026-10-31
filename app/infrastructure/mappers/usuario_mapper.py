from app.domain.entities import Usuario
from app.infrastructure.models import UsuarioModel


def usuario_a_dominio(modelo: UsuarioModel) -> Usuario:
    return Usuario(
        id=modelo.id,
        nombre=modelo.nombre,
        correo=modelo.correo,
        rol=modelo.rol,
        activo=modelo.activo,
    )


def usuario_a_modelo(entidad: Usuario) -> UsuarioModel:
    return UsuarioModel(
        id=entidad.id,
        nombre=entidad.nombre,
        correo=entidad.correo,
        rol=entidad.rol,
        activo=entidad.activo,
    )
