"""
Punto de entrada de la aplicación. Configura FastAPI y el manejo
estándar de errores para todos los endpoints.

Formato uniforme de error:
    {"error": {"code": str, "message": str, "details": list}}
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.domain.errores import (
    ConflictoError,
    CuentaBloqueada,
    NoAutenticado,
    Prohibido,
    RecursoNoEncontrado,
    ReglaNegocioError,
)
from app.infrastructure.config import CORS_ORIGINS
from app.presentation.routers import (
    auth_router,
    equipamiento_router,
    reserva_router,
    sala_router,
    usuario_router,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("reservas.api")

app = FastAPI(
    title="Sistema de Reservas de Salas y Laboratorios",
    description=(
        "API REST para gestionar usuarios, salas, equipamiento y reservas. "
        "Incluye autenticación JWT con refresh rotado, recuperación de contraseña "
        "de un solo uso, roles, filtro, orden y paginación, y errores con formato "
        'uniforme: {"error": {"code", "message", "details"}}.'
    ),
    version="1.0.0",
    contact={"name": "Grupo 06 - Desarrollo de Backend ICINF1108"},
)

# CORS con orígenes explícitos: no se admite "*" cuando se envían credenciales.
# Los orígenes se configuran con CORS_ORIGINS (separados por coma).
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(auth_router.router)
app.include_router(sala_router.router)
app.include_router(usuario_router.router)
app.include_router(equipamiento_router.router)
app.include_router(reserva_router.router)


def error_response(code: str, message: str, details: list, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
            }
        },
    )


def _detalles_validacion(exc: RequestValidationError) -> list[dict]:
    """Resume los errores de Pydantic sin reenviar los valores del cliente.

    `exc.errors()` incluye `input` y `ctx`; si el cuerpo trae una contraseña,
    un token o un secreto, esos valores quedarían en la respuesta 422. Solo se
    conservan la ubicación, el mensaje y el tipo de error.
    """
    return [
        {
            "loc": list(error.get("loc", [])),
            "msg": str(error.get("msg", "")),
            "type": str(error.get("type", "")),
        }
        for error in exc.errors()
    ]


@app.get("/", tags=["Estado"], summary="Estado del servicio")
def estado_servicio():
    return {"servicio": "reservas-uct", "version": "1.0.0", "estado": "operativo"}


# Errores de validación de Pydantic (esquema/tipos) -> 422
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(
        code="VALIDATION_ERROR",
        message="Los datos enviados no cumplen el formato esperado.",
        details=_detalles_validacion(exc),
        status_code=422,
    )


# Recurso inexistente -> 404
@app.exception_handler(RecursoNoEncontrado)
async def recurso_no_encontrado_handler(request: Request, exc: RecursoNoEncontrado):
    return error_response(
        code="RESOURCE_NOT_FOUND",
        message=str(exc),
        details=[],
        status_code=404,
    )


# Conflicto con el estado actual (solapamiento, sala en mantenimiento) -> 409
@app.exception_handler(ConflictoError)
async def conflicto_handler(request: Request, exc: ConflictoError):
    return error_response(
        code="CONFLICT",
        message=str(exc),
        details=[],
        status_code=409,
    )


# Falta el token o es inválido/expirado -> 401
@app.exception_handler(NoAutenticado)
async def no_autenticado_handler(request: Request, exc: NoAutenticado):
    return JSONResponse(
        status_code=401,
        content={
            "error": {
                "code": "UNAUTHORIZED",
                "message": str(exc),
                "details": [],
            }
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


# Autenticado pero sin permisos, o cuenta bloqueada -> 403
@app.exception_handler(Prohibido)
async def prohibido_handler(request: Request, exc: Prohibido):
    return error_response(
        code="FORBIDDEN",
        message=str(exc),
        details=[],
        status_code=403,
    )


@app.exception_handler(CuentaBloqueada)
async def cuenta_bloqueada_handler(request: Request, exc: CuentaBloqueada):
    return error_response(
        code="ACCOUNT_LOCKED",
        message=str(exc),
        details=[],
        status_code=403,
    )


# Violación de una regla de negocio -> 400
@app.exception_handler(ReglaNegocioError)
async def regla_negocio_handler(request: Request, exc: ReglaNegocioError):
    return error_response(
        code="BUSINESS_RULE_VIOLATION",
        message=str(exc),
        details=[],
        status_code=400,
    )


# Respaldo: cualquier ValueError suelto se trata como regla de negocio -> 400
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return error_response(
        code="BUSINESS_RULE_VIOLATION",
        message=str(exc),
        details=[],
        status_code=400,
    )


# Respaldo final: ninguna excepción no controlada escapa como 500 en texto plano.
@app.exception_handler(Exception)
async def error_interno_handler(request: Request, exc: Exception):
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return error_response(
        code="INTERNAL_ERROR",
        message="Ocurrió un error interno. El equipo fue notificado y revisará el registro.",
        details=[],
        status_code=500,
    )
