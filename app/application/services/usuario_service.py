"""
Casos de uso de Usuario: lógica de negocio y coordinación con el repositorio.
"""

from dataclasses import replace

from sqlalchemy.orm import Session

from app.domain.entities import RolUsuario, Usuario
from app.domain.errores import ConflictoError, RecursoNoEncontrado, ReglaNegocioError
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.security.passwords import errores_de_password, hash_password
from app.presentation.schemas.dtos import UsuarioCreate


def _validar_password(password: str) -> None:
    errores = errores_de_password(password)
    if errores:
        raise ReglaNegocioError(
            "La contraseña no cumple la política de seguridad: " + " ".join(errores)
        )


def crear_usuario(db: Session, data: UsuarioCreate) -> Usuario:
    repo = UsuarioRepository(db)
    correo = data.correo.lower().strip()

    # Regla de negocio: el correo debe ser único
    if any(u.correo.lower() == correo for u in repo.listar()):
        raise ConflictoError(f"Ya existe un usuario con el correo {data.correo}.")
    _validar_password(data.password)

    nuevo = Usuario(
        id=0,  # el repositorio asigna el ID real
        nombre=data.nombre,
        correo=correo,
        rol=data.rol,
        activo=True,
        password_hash=hash_password(data.password),
    )
    return repo.crear(nuevo)


def listar_usuarios(db: Session) -> list[Usuario]:
    return UsuarioRepository(db).listar()


def obtener_usuario(db: Session, usuario_id: int) -> Usuario:
    usuario = UsuarioRepository(db).obtener_por_id(usuario_id)
    if usuario is None:
        raise RecursoNoEncontrado(f"No existe un usuario con ID {usuario_id}.")
    return usuario


def cambiar_rol(db: Session, usuario_id: int, rol: RolUsuario) -> Usuario:
    usuario = obtener_usuario(db, usuario_id)
    return UsuarioRepository(db).actualizar(replace(usuario, rol=rol))
