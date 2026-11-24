"""Pruebas de integración del módulo de autenticación."""

from urllib.parse import parse_qs, urlparse

from tests.conftest import ADMIN, ESTUDIANTE


def _token_de_enlace(enlace: str) -> str:
    return parse_qs(urlparse(enlace).query)["token"][0]


def test_registro_login_y_perfil(client):
    registro = client.post(
        "/auth/registro",
        json={
            "nombre": "Tomás Mardones",
            "correo": "tomas@alu.uct.cl",
            "password": "Prueba.2026.Segura!",
        },
    )
    assert registro.status_code == 201, registro.text
    assert registro.json()["rol"] == "estudiante"
    assert "password" not in registro.json() and "password_hash" not in registro.json()

    login = client.post(
        "/auth/login",
        json={"correo": "tomas@alu.uct.cl", "password": "Prueba.2026.Segura!"},
    )
    assert login.status_code == 200
    cuerpo = login.json()
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["expires_in"] > 0
    assert cuerpo["refresh_token"]

    perfil = client.get("/auth/me", headers={"Authorization": f"Bearer {cuerpo['access_token']}"})
    assert perfil.status_code == 200
    assert perfil.json()["correo"] == "tomas@alu.uct.cl"


def test_registro_con_password_debil_es_rechazado(client):
    respuesta = client.post(
        "/auth/registro",
        json={"nombre": "Débil", "correo": "debil@alu.uct.cl", "password": "123456"},
    )
    assert respuesta.status_code == 400
    assert respuesta.json()["error"]["code"] == "BUSINESS_RULE_VIOLATION"


def test_login_incorrecto_y_bloqueo_tras_cinco_intentos(client):
    for _ in range(4):
        respuesta = client.post(
            "/auth/login",
            json={"correo": ESTUDIANTE["correo"], "password": "Incorrecta.2026!"},
        )
        assert respuesta.status_code == 401
        assert respuesta.json()["error"]["code"] == "UNAUTHORIZED"

    quinto = client.post(
        "/auth/login",
        json={"correo": ESTUDIANTE["correo"], "password": "Incorrecta.2026!"},
    )
    assert quinto.status_code == 403
    assert quinto.json()["error"]["code"] == "ACCOUNT_LOCKED"

    # Incluso con la contraseña correcta, la cuenta sigue bloqueada.
    bloqueado = client.post("/auth/login", json=ESTUDIANTE)
    assert bloqueado.status_code == 403


def test_me_sin_token_responde_401(client):
    respuesta = client.get("/auth/me")
    assert respuesta.status_code == 401
    assert respuesta.headers["www-authenticate"] == "Bearer"
    assert respuesta.json()["error"]["code"] == "UNAUTHORIZED"


def test_refresh_rota_el_token_y_detecta_reutilizacion(client):
    login = client.post("/auth/login", json=ESTUDIANTE).json()

    primera_rotacion = client.post("/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert primera_rotacion.status_code == 200
    nuevo_refresh = primera_rotacion.json()["refresh_token"]
    assert nuevo_refresh != login["refresh_token"]

    reutilizado = client.post("/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert reutilizado.status_code == 401
    assert "sesiones" in reutilizado.json()["error"]["message"]

    # La detección de reutilización cierra también el token vigente.
    revocado = client.post("/auth/refresh", json={"refresh_token": nuevo_refresh})
    assert revocado.status_code == 401


def test_logout_revoca_el_refresh(client):
    login = client.post("/auth/login", json=ESTUDIANTE).json()
    salida = client.post("/auth/logout", json={"refresh_token": login["refresh_token"]})
    assert salida.status_code == 204

    reuso = client.post("/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert reuso.status_code == 401


def test_recuperacion_enlace_de_un_solo_uso(client):
    solicitud = client.post("/auth/recuperacion/solicitar", json={"correo": ESTUDIANTE["correo"]})
    assert solicitud.status_code == 202
    enlace = solicitud.json()["enlace_recuperacion"]
    assert enlace and "token=" in enlace

    token = _token_de_enlace(enlace)
    primera = client.post(
        "/auth/recuperacion/restablecer",
        json={"token": token, "password_nueva": "Nueva.2026.Clave!"},
    )
    assert primera.status_code == 200

    segunda = client.post(
        "/auth/recuperacion/restablecer",
        json={"token": token, "password_nueva": "Otra.2026.Clave!"},
    )
    assert segunda.status_code == 401
    assert "utilizado" in segunda.json()["error"]["message"]

    vieja = client.post("/auth/login", json=ESTUDIANTE)
    assert vieja.status_code == 401
    nueva = client.post(
        "/auth/login",
        json={"correo": ESTUDIANTE["correo"], "password": "Nueva.2026.Clave!"},
    )
    assert nueva.status_code == 200


def test_restablecer_invalida_sesiones_previas(client):
    login = client.post("/auth/login", json=ESTUDIANTE).json()

    enlace = client.post(
        "/auth/recuperacion/solicitar", json={"correo": ESTUDIANTE["correo"]}
    ).json()["enlace_recuperacion"]
    token = _token_de_enlace(enlace)
    assert (
        client.post(
            "/auth/recuperacion/restablecer",
            json={"token": token, "password_nueva": "Nueva.2026.Clave!"},
        ).status_code
        == 200
    )

    # El refresh emitido antes del cambio ya no sirve.
    reuso = client.post("/auth/refresh", json={"refresh_token": login["refresh_token"]})
    assert reuso.status_code == 401


def test_solicitud_de_correo_inexistente_no_revela_informacion(client):
    respuesta = client.post("/auth/recuperacion/solicitar", json={"correo": "nadie@alu.uct.cl"})
    assert respuesta.status_code == 202
    assert respuesta.json()["enlace_recuperacion"] is None
    assert "Si el correo está registrado" in respuesta.json()["mensaje"]


def test_registro_publico_no_permite_escalar_rol(client):
    respuesta = client.post(
        "/auth/registro",
        json={
            "nombre": "Intruso",
            "correo": "intruso@alu.uct.cl",
            "password": "Prueba.2026.Segura!",
            "rol": "administrador",
        },
    )
    assert respuesta.status_code == 201
    assert respuesta.json()["rol"] == "estudiante"


def test_admin_puede_crear_usuarios_y_otro_rol_no(client, admin_headers, docente_headers):
    permitido = client.post(
        "/usuarios",
        headers=admin_headers,
        json={
            "nombre": "Jesús Huentemil",
            "correo": "jesus@uct.cl",
            "rol": "docente",
            "password": "Prueba.2026.Segura!",
        },
    )
    assert permitido.status_code == 201

    denegado = client.post(
        "/usuarios",
        headers=docente_headers,
        json={
            "nombre": "Sin Permiso",
            "correo": "sinpermiso@uct.cl",
            "rol": "estudiante",
            "password": "Prueba.2026.Segura!",
        },
    )
    assert denegado.status_code == 403
    assert denegado.json()["error"]["code"] == "FORBIDDEN"


def test_login_de_administrador_del_seeder(client):
    respuesta = client.post("/auth/login", json=ADMIN)
    assert respuesta.status_code == 200
    perfil = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {respuesta.json()['access_token']}"},
    )
    assert perfil.json()["rol"] == "administrador"
