from app.domain.entities import Usuario
from app.infrastructure.models import UsuarioModel


def usuario_a_dominio(modelo: UsuarioModel) -> Usuario:
    return Usuario(
        id=modelo.id,
        nombre=modelo.nombre,
        correo=modelo.correo,
        rol=modelo.rol,
        activo=modelo.activo,
        password_hash=modelo.password_hash or "",
        intentos_fallidos=modelo.intentos_fallidos or 0,
        bloqueado_hasta=modelo.bloqueado_hasta,
    )


def usuario_a_modelo(entidad: Usuario) -> UsuarioModel:
    return UsuarioModel(
        id=entidad.id,
        nombre=entidad.nombre,
        correo=entidad.correo,
        rol=entidad.rol,
        activo=entidad.activo,
        password_hash=entidad.password_hash,
        intentos_fallidos=entidad.intentos_fallidos,
        bloqueado_hasta=entidad.bloqueado_hasta,
    )
