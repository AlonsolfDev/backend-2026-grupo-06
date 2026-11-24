"""
Entidades del dominio del sistema de reservas.

Relación 1:N definida:
- Un Usuario puede tener muchas Reservas.
- Una Sala puede tener muchas Reservas.
- Una Sala puede tener muchos Equipamientos asociados.

Las entidades son independientes de la base de datos: no conocen SQLAlchemy.
Los atributos con valor por defecto permiten construir la entidad sin repetir
datos que la capa de persistencia completa (por ejemplo, el ID asignado).
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class RolUsuario(str, Enum):
    ADMINISTRADOR = "administrador"
    DOCENTE = "docente"
    ESTUDIANTE = "estudiante"


class EstadoSala(str, Enum):
    DISPONIBLE = "disponible"
    MANTENIMIENTO = "mantenimiento"


class EstadoEquipamiento(str, Enum):
    DISPONIBLE = "disponible"
    DANADO = "danado"


class EstadoReserva(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"


class PropositoToken(str, Enum):
    """Propósito exclusivo de cada token emitido por la aplicación."""

    ACCESO = "acceso"
    RECUPERACION = "recuperacion"


@dataclass
class Usuario:
    id: int
    nombre: str
    correo: str
    rol: RolUsuario
    activo: bool = True
    # Credenciales. El hash NUNCA viaja al cliente ni se registra en logs.
    password_hash: str = ""
    intentos_fallidos: int = 0
    bloqueado_hasta: datetime | None = None


@dataclass
class Sala:
    id: int
    nombre: str
    capacidad: int
    ubicacion: str
    estado: EstadoSala = EstadoSala.DISPONIBLE


@dataclass
class Equipamiento:
    id: int
    nombre: str
    tipo: str
    estado: EstadoEquipamiento
    sala_id: int  # relación N:1 hacia Sala (Sala 1:N Equipamiento)
    descripcion: str = ""


@dataclass
class Reserva:
    id: int
    usuario_id: int  # relación N:1 hacia Usuario (Usuario 1:N Reserva)
    sala_id: int  # relación N:1 hacia Sala (Sala 1:N Reserva)
    fecha_inicio: datetime
    fecha_fin: datetime
    proposito: str = ""
    num_asistentes: int = 0
    estado: EstadoReserva = EstadoReserva.PENDIENTE


@dataclass
class RefreshToken:
    """Token de refresco opaco. En la base solo se guarda su hash SHA-256."""

    id: int
    usuario_id: int
    token_hash: str
    expira_en: datetime
    revocado: bool = False
    creado_en: datetime | None = None


@dataclass
class RecuperacionToken:
    """Registro del `jti` de un JWT de recuperación para garantizar uso único."""

    id: int
    usuario_id: int
    jti: str
    expira_en: datetime
    usado: bool = False
    creado_en: datetime | None = None
