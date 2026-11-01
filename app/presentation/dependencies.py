"""
Dependencias por solicitud: entrega una sesión de BD a cada endpoint
y la cierra al terminar.
"""
from typing import Generator

from sqlalchemy.orm import Session

from app.infrastructure.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()