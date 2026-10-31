"""
Punto de entrada de la aplicación. Configura FastAPI y el manejo
estándar de errores para todos los endpoints.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

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
        details=exc.errors(),
        status_code=422,
    )


# Errores de reglas de negocio (los que lanzan ValueError) -> 400
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return error_response(
        code="BUSINESS_RULE_VIOLATION",
        message=str(exc),
        details=[],
        status_code=400,
    )