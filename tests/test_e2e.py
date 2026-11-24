"""Pruebas end-to-end: recorridos completos de la API como la usaría un cliente."""

from urllib.parse import parse_qs, urlparse

from tests.conftest import ADMIN, ESTUDIANTE, PASSWORD_DEMO


def test_e2e_flujo_completo_de_reserva(client):
    # 1. El administrador inicia sesión y prepara una sala con equipamiento.
    admin = client.post("/auth/login", json=ADMIN).json()
    admin_headers = {"Authorization": f"Bearer {admin['access_token']}"}

    sala = client.post(
        "/salas",
        headers=admin_headers,
        json={"nombre": "Laboratorio 3", "capacidad": 8, "ubicacion": "Edificio C"},
    )
    assert sala.status_code == 201
    sala_id = sala.json()["id"]

    equipo = client.post(
        "/equipamientos",
        headers=admin_headers,
        json={
            "nombre": "Notebook de laboratorio",
            "tipo": "computador",
            "sala_id": sala_id,
            "descripcion": "Notebook con Ubuntu",
        },
    )
    assert equipo.status_code == 201

    # 2. Un estudiante se registra e inicia sesión.
    assert (
        client.post(
            "/auth/registro",
            json={
                "nombre": "Alonso Lantaño",
                "correo": "alonso@alu.uct.cl",
                "password": "Prueba.2026.Segura!",
            },
        ).status_code
        == 201
    )
    estudiante = client.post(
        "/auth/login",
        json={"correo": "alonso@alu.uct.cl", "password": "Prueba.2026.Segura!"},
    ).json()
    est_headers = {"Authorization": f"Bearer {estudiante['access_token']}"}

    # 3. Consulta disponibilidad y reserva.
    disponibilidad = client.get(
        f"/salas/{sala_id}/disponibilidad",
        params={
            "fecha_inicio": "2026-12-22T14:00:00",
            "fecha_fin": "2026-12-22T16:00:00",
        },
    )
    assert disponibilidad.json()["disponible"] is True

    reserva = client.post(
        "/reservas",
        headers=est_headers,
        json={
            "usuario_id": 1,  # se ignora: el estudiante reserva a su nombre
            "sala_id": sala_id,
            "fecha_inicio": "2026-12-22T14:00:00",
            "fecha_fin": "2026-12-22T16:00:00",
            "proposito": "Proyecto de Backend",
            "num_asistentes": 4,
        },
    )
    assert reserva.status_code == 201, reserva.text
    reserva_id = reserva.json()["id"]
    assert reserva.json()["usuario_id"] != 1

    # 4. Confirma y verifica que la sala deja de estar disponible.
    assert client.patch(f"/reservas/{reserva_id}/confirmar", headers=est_headers).status_code == 200
    ocupada = client.get(
        f"/salas/{sala_id}/disponibilidad",
        params={
            "fecha_inicio": "2026-12-22T15:00:00",
            "fecha_fin": "2026-12-22T17:00:00",
        },
    )
    assert ocupada.json()["disponible"] is False

    # 5. Se lista y se cancela; la evidencia queda en la respuesta.
    listado = client.get("/reservas", params={"sala_id": sala_id, "estado": "confirmada"})
    assert listado.json()["total"] == 1
    assert client.patch(f"/reservas/{reserva_id}/cancelar", headers=est_headers).status_code == 200


def test_e2e_matriz_de_permisos_401_403_200(client):
    docente = client.post("/auth/login", json=ESTUDIANTE).json()
    est_headers = {"Authorization": f"Bearer {docente['access_token']}"}
    admin = client.post("/auth/login", json=ADMIN).json()
    admin_headers = {"Authorization": f"Bearer {admin['access_token']}"}

    sala = {"nombre": "Sala Matriz", "capacidad": 10, "ubicacion": "Edificio D"}

    # Sin token -> 401
    assert client.post("/salas", json=sala).status_code == 401
    # Token de estudiante -> 403
    assert client.post("/salas", json=sala, headers=est_headers).status_code == 403
    # Token de administrador -> 201
    assert client.post("/salas", json=sala, headers=admin_headers).status_code == 201

    # Lecturas públicas -> 200 sin token
    assert client.get("/salas").status_code == 200
    assert client.get("/reservas").status_code == 200
    assert client.get("/equipamientos").status_code == 200

    # Listado de usuarios: solo administrador
    assert client.get("/usuarios").status_code == 401
    assert client.get("/usuarios", headers=est_headers).status_code == 403
    assert client.get("/usuarios", headers=admin_headers).status_code == 200


def test_e2e_recuperacion_de_password_completa(client):
    # 1. Sesión activa antes de la recuperación.
    sesion_previa = client.post("/auth/login", json=ESTUDIANTE).json()

    # 2. Solicitud de recuperación (en dev el enlace vuelve en el JSON).
    solicitud = client.post("/auth/recuperacion/solicitar", json={"correo": ESTUDIANTE["correo"]})
    assert solicitud.status_code == 202
    enlace = solicitud.json()["enlace_recuperacion"]
    token = parse_qs(urlparse(enlace).query)["token"][0]

    # 3. Restablecimiento con una contraseña válida.
    cambio = client.post(
        "/auth/recuperacion/restablecer",
        json={"token": token, "password_nueva": "Defensa.2026.Ok!"},
    )
    assert cambio.status_code == 200

    # 4. La contraseña anterior ya no sirve y la nueva sí.
    assert client.post("/auth/login", json=ESTUDIANTE).status_code == 401
    nuevo_login = client.post(
        "/auth/login",
        json={"correo": ESTUDIANTE["correo"], "password": "Defensa.2026.Ok!"},
    )
    assert nuevo_login.status_code == 200
    assert nuevo_login.json()["access_token"]

    # 5. La sesión previa quedó invalidada.
    revocada = client.post("/auth/refresh", json={"refresh_token": sesion_previa["refresh_token"]})
    assert revocada.status_code == 401

    # 6. El enlace es de un solo uso.
    assert (
        client.post(
            "/auth/recuperacion/restablecer",
            json={"token": token, "password_nueva": PASSWORD_DEMO},
        ).status_code
        == 401
    )
