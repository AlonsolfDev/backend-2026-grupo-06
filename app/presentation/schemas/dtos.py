"""
DTOs (esquemas de entrada/salida) para las 4 entidades del dominio.
"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nombre": "Ana Pérez",
                    "correo": "ana.perez@uct.cl",
                    "rol": "docente",
                }
            ]
        }
    )


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    rol: RolUsuario
    activo: bool

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "nombre": "Ana Pérez",
                    "correo": "ana.perez@uct.cl",
                    "rol": "docente",
                    "activo": True,
                }
            ]
        }
    )


class SalaCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    capacidad: int = Field(gt=0, le=500)
    ubicacion: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nombre": "Sala A101",
                    "capacidad": 30,
                    "ubicacion": "Edificio A, piso 1",
                }
            ]
        }
    )


class SalaOut(SalaCreate):
    id: int
    estado: EstadoSala

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "nombre": "Sala A101",
                    "capacidad": 30,
                    "ubicacion": "Edificio A, piso 1",
                    "estado": "disponible",
                }
            ]
        }
    )


class EquipamientoCreate(BaseModel):
    nombre: str
    tipo: str
    sala_id: int
    descripcion: str = ""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nombre": "Proyector Epson",
                    "tipo": "proyector",
                    "sala_id": 1,
                    "descripcion": "Proyector HDMI de 3000 lúmenes",
                }
            ]
        }
    )


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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "nombre": "Proyector Epson",
                    "tipo": "proyector",
                    "sala_id": 1,
                    "descripcion": "Proyector HDMI de 3000 lúmenes",
                    "estado": "disponible",
                }
            ]
        }
    )


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

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "usuario_id": 1,
                    "sala_id": 1,
                    "fecha_inicio": "2026-11-12T10:00:00",
                    "fecha_fin": "2026-11-12T12:00:00",
                }
            ]
        }
    )


class ReservaOut(ReservaCreate):
    id: int
    estado: EstadoReserva

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "usuario_id": 1,
                    "sala_id": 1,
                    "fecha_inicio": "2026-11-12T10:00:00",
                    "fecha_fin": "2026-11-12T12:00:00",
                    "estado": "pendiente",
                }
            ]
        }
    )


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


class ErrorDetalle(BaseModel):
    code: str = Field(examples=["RESOURCE_NOT_FOUND"])
    message: str = Field(examples=["No existe una sala con ID 999."])
    details: list = Field(default_factory=list)


class ErrorOut(BaseModel):
    error: ErrorDetalle