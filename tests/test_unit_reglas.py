"""Pruebas unitarias de las reglas de negocio y la seguridad de contraseñas.

No tocan base de datos ni HTTP: prueban funciones puras del dominio.
"""

from datetime import datetime

import pytest

from app.domain.entities import (
    Equipamiento,
    EstadoEquipamiento,
    EstadoReserva,
    EstadoSala,
    Reserva,
    Sala,
)
from app.domain.errores import ConflictoError, ReglaNegocioError
from app.domain.reglas_negocio import (
    validar_capacidad_sala,
    validar_disponibilidad_sala,
    validar_equipamiento_disponible,
    validar_fechas_reserva,
    validar_sala_operativa,
)
from app.infrastructure.security.passwords import (
    errores_de_password,
    hash_password,
    verificar_password,
)


def test_fechas_invalidas_lanza_regla_negocio():
    with pytest.raises(ReglaNegocioError):
        validar_fechas_reserva(datetime(2026, 12, 1, 12, 0), datetime(2026, 12, 1, 10, 0))


def test_solapamiento_con_reserva_confirmada():
    existente = Reserva(
        id=1,
        usuario_id=1,
        sala_id=1,
        fecha_inicio=datetime(2026, 12, 1, 10, 0),
        fecha_fin=datetime(2026, 12, 1, 12, 0),
        estado=EstadoReserva.CONFIRMADA,
    )
    with pytest.raises(ConflictoError):
        validar_disponibilidad_sala(
            1, datetime(2026, 12, 1, 11, 0), datetime(2026, 12, 1, 13, 0), [existente]
        )


def test_reserva_pendiente_no_bloquea_el_horario():
    pendiente = Reserva(
        id=1,
        usuario_id=1,
        sala_id=1,
        fecha_inicio=datetime(2026, 12, 1, 10, 0),
        fecha_fin=datetime(2026, 12, 1, 12, 0),
        estado=EstadoReserva.PENDIENTE,
    )
    # No lanza: solo las reservas confirmadas bloquean el horario.
    validar_disponibilidad_sala(
        1, datetime(2026, 12, 1, 11, 0), datetime(2026, 12, 1, 13, 0), [pendiente]
    )


def test_equipamiento_danado_impide_reservar():
    equipo = Equipamiento(
        id=1,
        nombre="Proyector",
        tipo="audiovisual",
        estado=EstadoEquipamiento.DANADO,
        sala_id=1,
    )
    with pytest.raises(ReglaNegocioError, match="dañado"):
        validar_equipamiento_disponible([equipo])


def test_capacidad_excedida_lanza_regla_negocio():
    sala = Sala(id=1, nombre="Sala Pequeña", capacidad=10, ubicacion="A")
    with pytest.raises(ReglaNegocioError, match="capacidad"):
        validar_capacidad_sala(sala, 11)


def test_sala_en_mantenimiento_no_es_reservable():
    sala = Sala(
        id=1,
        nombre="Sala A",
        capacidad=20,
        ubicacion="A",
        estado=EstadoSala.MANTENIMIENTO,
    )
    with pytest.raises(ConflictoError, match="mantenimiento"):
        validar_sala_operativa(sala)


def test_politica_de_password_y_hash_argon2id():
    assert errores_de_password("corta")  # demasiado corta y sin complejidad
    assert errores_de_password("Demo.2026.Segura!") == []

    hash_generado = hash_password("Demo.2026.Segura!")
    assert hash_generado.startswith("$argon2id$")
    assert verificar_password("Demo.2026.Segura!", hash_generado) is True
    assert verificar_password("Otra.2026.Clave!", hash_generado) is False
