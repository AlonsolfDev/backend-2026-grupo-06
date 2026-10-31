"""
DTOs (esquemas de entrada/salida) para las 4 entidades del dominio.
"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


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


class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    correo: EmailStr
    rol: RolUsuario


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    rol: RolUsuario
    activo: bool


class SalaCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    capacidad: int = Field(gt=0, le=500)
    ubicacion: str


class SalaOut(SalaCreate):
    id: int
    estado: EstadoSala


class EquipamientoCreate(BaseModel):
    nombre: str
    tipo: str
    sala_id: int


class EquipamientoOut(EquipamientoCreate):
    id: int
    estado: EstadoEquipamiento


class ReservaCreate(BaseModel):
    usuario_id: int
    sala_id: int
    fecha_inicio: datetime
    fecha_fin: datetime


class ReservaOut(ReservaCreate):
    id: int
    estado: EstadoReserva
class SalaPaginada(BaseModel):
    items: list[SalaOut]
    total: int
    pagina: int
    limite: int
    total_paginas: int

    