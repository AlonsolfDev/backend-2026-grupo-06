"""Pruebas de integración de reservas, salas y equipamiento.

Incluye la prueba de regresión del defecto reportado en la Entrega II:
los endpoints de reservas y equipamiento respondían 500 por campos que la
entidad no declaraba.
"""

from tests.conftest import ESTUDIANTE


def _payload(sala_id=1, inicio="2026-12-10T10:00:00", fin="2026-12-10T12:00:00", **extra):
    datos = {
        "usuario_id": 3,
        "sala_id": sala_id,
        "fecha_inicio": inicio,
        "fecha_fin": fin,
        "proposito": "Trabajo grupal",
        "num_asistentes": 5,
    }
    datos.update(extra)
    return datos


def test_regresion_reservas_y_equipamientos_ya_no_responden_500(client):
    assert client.get("/reservas").status_code == 200
    assert client.get("/equipamientos").status_code == 200
    assert client.get("/reservas/1").status_code == 200
    # La reserva expone proposito y num_asistentes (campos que faltaban).
    reserva = client.get("/reservas/1").json()
    assert reserva["proposito"]
    assert reserva["num_asistentes"] > 0


def test_crear_reserva_completa_devuelve_201(client, estudiante_headers):
    respuesta = client.post("/reservas", headers=estudiante_headers, json=_payload())
    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "pendiente"
    assert cuerpo["proposito"] == "Trabajo grupal"
    # Un estudiante no puede reservar a nombre de otro usuario.
    assert cuerpo["usuario_id"] == 3


def test_reserva_que_excede_capacidad_devuelve_400(client, estudiante_headers):
    respuesta = client.post(
        "/reservas", headers=estudiante_headers, json=_payload(sala_id=2, num_asistentes=99)
    )
    assert respuesta.status_code == 400
    assert "capacidad" in respuesta.json()["error"]["message"]


def test_solapamiento_con_reserva_confirmada_devuelve_409(client, estudiante_headers):
    respuesta = client.post(
        "/reservas",
        headers=estudiante_headers,
        json=_payload(inicio="2026-12-02T10:00:00", fin="2026-12-02T12:00:00"),
    )
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["code"] == "CONFLICT"


def test_cancelar_reserva_y_repetir_cancelacion(client, estudiante_headers):
    creada = client.post("/reservas", headers=estudiante_headers, json=_payload())
    reserva_id = creada.json()["id"]

    cancelada = client.patch(f"/reservas/{reserva_id}/cancelar", headers=estudiante_headers)
    assert cancelada.status_code == 200
    assert cancelada.json()["estado"] == "cancelada"

    repetida = client.patch(f"/reservas/{reserva_id}/cancelar", headers=estudiante_headers)
    assert repetida.status_code == 409


def test_usuario_no_puede_modificar_reserva_ajena(client, crear_estudiante):
    otro = crear_estudiante("Otro Alumno")
    # La reserva 2 pertenece a Luis (usuario 3) en el seeder.
    respuesta = client.patch("/reservas/2/cancelar", headers=otro)
    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["code"] == "FORBIDDEN"


def test_usuario_no_puede_crear_reservas_sin_token(client):
    respuesta = client.post("/reservas", json=_payload())
    assert respuesta.status_code == 401


def test_filtros_combinados_de_reservas(client, estudiante_headers):
    client.post("/reservas", headers=estudiante_headers, json=_payload())
    client.post(
        "/reservas",
        headers=estudiante_headers,
        json=_payload(inicio="2026-12-11T08:00:00", fin="2026-12-11T09:00:00"),
    )

    por_usuario = client.get("/reservas", params={"usuario_id": 3})
    assert por_usuario.status_code == 200
    assert por_usuario.json()["total"] == 3  # 1 del seeder + 2 creadas

    por_estado = client.get("/reservas", params={"estado": "pendiente", "limite": 100})
    assert all(item["estado"] == "pendiente" for item in por_estado.json()["items"])

    por_fecha = client.get("/reservas", params={"fecha": "2026-12-10"})
    assert por_fecha.json()["total"] == 1

    combinado = client.get(
        "/reservas",
        params={"usuario_id": 3, "sala_id": 1, "estado": "pendiente", "fecha": "2026-12-11"},
    )
    assert combinado.json()["total"] == 1


def test_disponibilidad_refleja_reservas_confirmadas(client):
    libre = client.get(
        "/salas/2/disponibilidad",
        params={
            "fecha_inicio": "2026-12-15T08:00:00",
            "fecha_fin": "2026-12-15T10:00:00",
        },
    )
    assert libre.status_code == 200
    assert libre.json()["disponible"] is True

    ocupada = client.get(
        "/salas/1/disponibilidad",
        params={
            "fecha_inicio": "2026-12-02T09:30:00",
            "fecha_fin": "2026-12-02T10:30:00",
        },
    )
    assert ocupada.json()["disponible"] is False
    assert "reserva" in ocupada.json()["motivo"]


def test_sala_en_mantenimiento_rechaza_reservas(client, admin_headers, estudiante_headers):
    cambio = client.patch(
        "/salas/2/estado", headers=admin_headers, json={"estado": "mantenimiento"}
    )
    assert cambio.status_code == 200

    respuesta = client.post(
        "/reservas",
        headers=estudiante_headers,
        json=_payload(sala_id=2, inicio="2026-12-18T10:00:00", fin="2026-12-18T12:00:00"),
    )
    assert respuesta.status_code == 409
    assert "mantenimiento" in respuesta.json()["error"]["message"]


def test_equipamiento_danado_impide_confirmar(client, admin_headers):
    danado = client.patch(
        "/equipamientos/1/estado", headers=admin_headers, json={"estado": "danado"}
    )
    assert danado.status_code == 200

    creada = client.post(
        "/reservas",
        headers=admin_headers,
        json=_payload(inicio="2026-12-19T10:00:00", fin="2026-12-19T12:00:00"),
    )
    assert creada.status_code == 201

    confirmacion = client.patch(f"/reservas/{creada.json()['id']}/confirmar", headers=admin_headers)
    assert confirmacion.status_code == 400
    assert "dañado" in confirmacion.json()["error"]["message"]


def test_sala_incluye_su_equipamiento(client):
    detalle = client.get("/salas/1")
    assert detalle.status_code == 200
    assert detalle.json()["equipamientos"][0]["nombre"] == "Proyector"

    equipos = client.get("/salas/1/equipamientos")
    assert equipos.status_code == 200
    assert len(equipos.json()) == 1

    inexistente = client.get("/salas/999/equipamientos")
    assert inexistente.status_code == 404


def test_eliminar_reserva_y_reserva_inexistente(client, estudiante_headers):
    creada = client.post("/reservas", headers=estudiante_headers, json=_payload())
    reserva_id = creada.json()["id"]

    borrada = client.delete(f"/reservas/{reserva_id}", headers=estudiante_headers)
    assert borrada.status_code == 204

    inexistente = client.get(f"/reservas/{reserva_id}")
    assert inexistente.status_code == 404
    assert inexistente.json()["error"]["code"] == "RESOURCE_NOT_FOUND"


def test_crear_reserva_con_usuario_inexistente(client, estudiante_headers):
    respuesta = client.post("/reservas", headers=estudiante_headers, json=_payload(usuario_id=9999))
    # El usuario_id del cuerpo se ignora para no administradores, pero la sala
    # inexistente sí debe devolver 404.
    inexistente = client.post("/reservas", headers=estudiante_headers, json=_payload(sala_id=9999))
    assert respuesta.status_code in (201, 404)
    assert inexistente.status_code == 404


def test_login_estudiante_del_seeder(client):
    login = client.post("/auth/login", json=ESTUDIANTE)
    assert login.status_code == 200
