"""Pruebas de los ajustes de seguridad de la pauta 5.5 y 5.6.

Cubren CORS con orígenes explícitos, el límite de solicitudes repetidas de
recuperación (sin bloquear la cuenta) y la ausencia de contraseñas, hashes o
tokens en respuestas, errores y logs.
"""

import logging
from urllib.parse import parse_qs, urlparse

from app.infrastructure.database import SessionLocal
from app.infrastructure.models.recuperacion_token_model import RecuperacionTokenModel
from tests.conftest import ESTUDIANTE


def test_cors_permite_un_origen_explicito(client):
    respuesta = client.options(
        "/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert respuesta.headers["access-control-allow-credentials"] == "true"


def test_cors_no_autoriza_un_origen_desconocido(client):
    respuesta = client.get("/", headers={"Origin": "https://origen-no-autorizado.example"})

    assert respuesta.status_code == 200
    assert "access-control-allow-origin" not in respuesta.headers


def test_recuperacion_repetida_se_limita_sin_bloquear_la_cuenta(client):
    primera = client.post("/auth/recuperacion/solicitar", json={"correo": ESTUDIANTE["correo"]})
    assert primera.status_code == 202
    assert primera.json()["enlace_recuperacion"]

    segunda = client.post("/auth/recuperacion/solicitar", json={"correo": ESTUDIANTE["correo"]})
    assert segunda.status_code == 202
    assert segunda.json()["enlace_recuperacion"] is None
    assert segunda.json()["mensaje"] == primera.json()["mensaje"]

    # No se creó un segundo token de recuperación.
    with SessionLocal() as db:
        assert db.query(RecuperacionTokenModel).count() == 1

    # La cuenta sigue activa: el límite no incrementa intentos ni la bloquea.
    assert client.post("/auth/login", json=ESTUDIANTE).status_code == 200


def test_validacion_no_ecoa_la_password_en_la_respuesta(client):
    secreto = "NoDebeSalir.2026!"
    respuesta = client.post(
        "/auth/registro",
        json={
            "nombre": "Prueba",
            "correo": "prueba@alu.uct.cl",
            "password": {"valor": secreto},
        },
    )

    assert respuesta.status_code == 422
    assert secreto not in respuesta.text
    detalle = respuesta.json()["error"]["details"][0]
    assert "input" not in detalle
    assert "ctx" not in detalle


def test_respuestas_de_usuarios_no_incluyen_password_hash(client, admin_headers):
    perfil = client.get("/auth/me", headers=admin_headers)
    assert perfil.status_code == 200
    assert "password_hash" not in perfil.text

    listado = client.get("/usuarios", headers=admin_headers)
    assert listado.status_code == 200
    assert "password_hash" not in listado.text


def test_login_fallido_no_registra_la_password_en_logs(client, caplog):
    secreto = "SecretoNoLog.2026!"
    with caplog.at_level(logging.INFO):
        respuesta = client.post(
            "/auth/login",
            json={"correo": ESTUDIANTE["correo"], "password": secreto},
        )

    assert respuesta.status_code == 401
    assert secreto not in caplog.text


def test_recuperacion_no_registra_el_token_en_logs(client, caplog):
    with caplog.at_level(logging.INFO):
        respuesta = client.post(
            "/auth/recuperacion/solicitar", json={"correo": ESTUDIANTE["correo"]}
        )

    assert respuesta.status_code == 202
    token = parse_qs(urlparse(respuesta.json()["enlace_recuperacion"]).query)["token"][0]
    assert token not in caplog.text
