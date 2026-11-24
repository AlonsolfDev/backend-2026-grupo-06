"""Fixtures compartidas por las pruebas automatizadas.

Cada prueba parte de una base SQLite limpia y sembrada, de modo que los
resultados no dependen del orden de ejecución.
"""

import os
import sys
import tempfile
import warnings

# La configuración de la base debe existir ANTES de importar la aplicación.
_DB_PATH = os.path.join(tempfile.gettempdir(), "reservas_pytest.db")
os.environ["DATABASE_URL"] = "sqlite:///" + _DB_PATH
os.environ["ENTORNO"] = "test"
os.environ["EXPONER_ENLACE_RECUPERACION"] = "true"
os.environ["SECRET_KEY"] = "clave-solo-para-pruebas-con-mas-de-32-bytes"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.infrastructure import models  # noqa: E402,F401
from app.infrastructure.database import Base, engine  # noqa: E402
from app.infrastructure.seeders.seed import PASSWORD_DEMO, seed  # noqa: E402
from app.main import app  # noqa: E402

warnings.filterwarnings("ignore", category=DeprecationWarning)

ADMIN = {"correo": "admin@uct.cl", "password": PASSWORD_DEMO}
DOCENTE = {"correo": "ana@uct.cl", "password": PASSWORD_DEMO}
ESTUDIANTE = {"correo": "luis@uct.cl", "password": PASSWORD_DEMO}


@pytest.fixture()
def client():
    """Cliente HTTP con una base de datos recién creada y sembrada."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    seed()
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _login(client, credenciales):
    respuesta = client.post("/auth/login", json=credenciales)
    assert respuesta.status_code == 200, respuesta.text
    return {"Authorization": f"Bearer {respuesta.json()['access_token']}"}


@pytest.fixture()
def admin_headers(client):
    return _login(client, ADMIN)


@pytest.fixture()
def estudiante_headers(client):
    return _login(client, ESTUDIANTE)


@pytest.fixture()
def docente_headers(client):
    return _login(client, DOCENTE)


def _crear_headers(client, nombre, correo):
    registro = client.post(
        "/auth/registro",
        json={"nombre": nombre, "correo": correo, "password": "Prueba.2026.Segura!"},
    )
    assert registro.status_code == 201, registro.text
    return _login(client, {"correo": correo, "password": "Prueba.2026.Segura!"})


@pytest.fixture()
def crear_estudiante(client):
    """Fábrica: crea un estudiante nuevo y devuelve sus cabeceras Bearer."""
    contador = {"n": 0}

    def _crear(nombre="Alumno Prueba"):
        contador["n"] += 1
        correo = f"alumno{contador['n']}@alu.uct.cl"
        return _crear_headers(client, nombre, correo)

    return _crear
