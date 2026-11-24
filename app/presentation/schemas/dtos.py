"""
DTOs (esquemas de entrada/salida) para las entidades del dominio y la
autenticación. Los DTO de salida nunca incluyen `password_hash`.
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


# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------
class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    correo: EmailStr
    rol: RolUsuario = RolUsuario.ESTUDIANTE
    password: str = Field(description="Contraseña en claro. Se almacena solo su hash Argon2id.")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nombre": "Ana Pérez",
                    "correo": "ana.perez@uct.cl",
                    "rol": "docente",
                    "password": "Demo.2026.Segura!",
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


class RolUpdate(BaseModel):
    rol: RolUsuario

    model_config = ConfigDict(json_schema_extra={"examples": [{"rol": "docente"}]})


# ---------------------------------------------------------------------------
# Salas
# ---------------------------------------------------------------------------
class SalaCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    capacidad: int = Field(gt=0, le=500)
    ubicacion: str = Field(min_length=2, max_length=120)

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


class EstadoSalaUpdate(BaseModel):
    estado: EstadoSala

    model_config = ConfigDict(json_schema_extra={"examples": [{"estado": "mantenimiento"}]})


# ---------------------------------------------------------------------------
# Equipamiento
# ---------------------------------------------------------------------------
class EquipamientoCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    tipo: str = Field(min_length=2, max_length=50)
    sala_id: int = Field(gt=0)
    descripcion: str = Field(default="", max_length=200)

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


class EstadoEquipamientoUpdate(BaseModel):
    estado: EstadoEquipamiento

    model_config = ConfigDict(json_schema_extra={"examples": [{"estado": "danado"}]})


class SalaDetalleOut(SalaOut):
    """Sala con su equipamiento asociado (relación 1:N)."""

    equipamientos: list[EquipamientoOut] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Reservas
# ---------------------------------------------------------------------------
class ReservaCreate(BaseModel):
    usuario_id: int = Field(gt=0)
    sala_id: int = Field(gt=0)
    fecha_inicio: datetime
    fecha_fin: datetime
    proposito: str = Field(min_length=3, max_length=200)
    num_asistentes: int = Field(gt=0)

    @model_validator(mode="after")
    def fecha_fin_posterior(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("fecha_fin debe ser posterior a fecha_inicio")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "usuario_id": 2,
                    "sala_id": 1,
                    "fecha_inicio": "2026-12-01T10:00:00",
                    "fecha_fin": "2026-12-01T12:00:00",
                    "proposito": "Trabajo grupal de Backend",
                    "num_asistentes": 5,
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
                    "usuario_id": 2,
                    "sala_id": 1,
                    "fecha_inicio": "2026-12-01T10:00:00",
                    "fecha_fin": "2026-12-01T12:00:00",
                    "proposito": "Trabajo grupal de Backend",
                    "num_asistentes": 5,
                    "estado": "pendiente",
                }
            ]
        }
    )


class DisponibilidadOut(BaseModel):
    sala_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
    disponible: bool
    motivo: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "sala_id": 1,
                    "fecha_inicio": "2026-12-01T10:00:00",
                    "fecha_fin": "2026-12-01T12:00:00",
                    "disponible": False,
                    "motivo": "La sala ya tiene una reserva confirmada en ese horario.",
                }
            ]
        }
    )


# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------
class RegistroRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    correo: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "nombre": "Diego Vásquez",
                    "correo": "diego.vasquez@alu.uct.cl",
                    "password": "Demo.2026.Segura!",
                }
            ]
        }
    )


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"correo": "admin@uct.cl", "password": "Demo.2026.Segura!"}]
        }
    )


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Segundos de vida del token de acceso")


class RecuperacionSolicitud(BaseModel):
    correo: EmailStr

    model_config = ConfigDict(json_schema_extra={"examples": [{"correo": "ana@uct.cl"}]})


class RecuperacionRespuesta(BaseModel):
    mensaje: str
    enlace_recuperacion: str | None = Field(
        default=None,
        description=(
            "Solo se incluye en entornos de prueba/prueba local. "
            "En producción el enlace viaja únicamente por correo."
        ),
    )


class RecuperacionRestablecer(BaseModel):
    token: str
    password_nueva: str


# ---------------------------------------------------------------------------
# Listados y errores
# ---------------------------------------------------------------------------
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


class MensajeOut(BaseModel):
    mensaje: str


class ErrorDetalle(BaseModel):
    code: str = Field(examples=["RESOURCE_NOT_FOUND"])
    message: str = Field(examples=["No existe una sala con ID 999."])
    details: list = Field(default_factory=list)


class ErrorOut(BaseModel):
    error: ErrorDetalle
