"""
Entidades del dominio del sistema de reservas.

Relación 1:N definida:
- Un Usuario puede tener muchas Reservas.
- Una Sala puede tener muchas Reservas.
- Una Sala puede tener muchos Equipamientos asociados.
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


@dataclass
class Usuario:
    id: int
    nombre: str
    correo: str
    rol: RolUsuario
    activo: bool = True


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


@dataclass
class Reserva:
    id: int
    usuario_id: int  # relación N:1 hacia Usuario (Usuario 1:N Reserva)
    sala_id: int      # relación N:1 hacia Sala (Sala 1:N Reserva)
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: EstadoReserva = EstadoReserva.PENDIENTE