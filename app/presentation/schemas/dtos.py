"""
DTOs (esquemas de entrada/salida) para las 4 entidades del dominio.
"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, model_validator
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
    descripcion: str = ""


class ReservaCreate(BaseModel):
    usuario_id: int
    sala_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
    proposito: str = Field(min_length=3, max_length=200)
    num_asistentes: int = Field(gt=0)

    @model_validator(mode="after")
    def fecha_fin_posterior(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
        return self

class EquipamientoOut(EquipamientoCreate):
    id: int
    estado: EstadoEquipamiento


class ReservaCreate(BaseModel):
    usuario_id: int
    sala_id: int
    fecha_inicio: datetime
    fecha_fin: datetime

    @model_validator(mode="after")
    def fecha_fin_posterior(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
        return self

class ReservaOut(ReservaCreate):
    id: int
    estado: EstadoReserva
class SalaPaginada(BaseModel):
    items: list[SalaOut]
    total: int
    pagina: int
    limite: int
    total_paginas: int


    

class ReservaPaginada(BaseModel):
    items: list[ReservaOut]
    total: int
    pagina: int
    limite: int
    total_paginas: int