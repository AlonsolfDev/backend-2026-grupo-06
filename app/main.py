"""
Punto de entrada de la aplicación. Configura FastAPI y el manejo
estándar de errores para todos los endpoints.
"""
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.domain.errores import ConflictoError, RecursoNoEncontrado, ReglaNegocioError
from app.presentation.routers import sala_router, usuario_router, equipamiento_router, reserva_router

app = FastAPI(title="Sistema de Reservas de Salas y Laboratorios")

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


# Errores de validación de Pydantic (esquema/tipos) -> 422
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(
        code="VALIDATION_ERROR",
        message="Los datos enviados no cumplen el formato esperado.",
        details=jsonable_encoder(exc.errors(), custom_encoder={Exception: str}),
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


# Conflicto con el estado actual (ej. sala ya reservada) -> 409
@app.exception_handler(ConflictoError)
async def conflicto_handler(request: Request, exc: ConflictoError):
    return error_response(
        code="CONFLICT",
        message=str(exc),
        details=[],
        status_code=409,
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