# Revisión de exposición de secretos (pauta 5.5 y 5.6)

Objetivo: comprobar que `password`, `password_hash`, tokens de acceso/refresh,
enlaces de recuperación y secretos de configuración no se filtren en DTO de
salida, errores HTTP, evidencias ni logs.

## 1. DTO y respuestas

| Elemento | Resultado | Evidencia |
|---|---|---|
| `UsuarioOut` | No declara `password` ni `password_hash` | `app/presentation/schemas/dtos.py` |
| `SalaOut`, `EquipamientoOut`, `ReservaOut` | No contienen credenciales | `app/presentation/schemas/dtos.py` |
| `ErrorOut` / `ErrorDetalle` | Solo `code`, `message`, `details` | `app/presentation/schemas/dtos.py` |
| `TokenPair` | Devuelve `access_token` y `refresh_token` solo en login/refresh; es el contrato necesario para autenticarse | `app/presentation/schemas/dtos.py` |
| `RecuperacionRespuesta` | El enlace solo se incluye si `EXPONER_ENLACE_RECUPERACION=true` (dev/test) | `app/application/services/auth_service.py` |

Las respuestas de `/auth/me` y `/usuarios` se comprueban en
`tests/test_seguridad.py::test_respuestas_de_usuarios_no_incluyen_password_hash`.

## 2. Errores HTTP

- **422 (validación)**: antes se devolvía `exc.errors()` completo, que incluye
  `input` y `ctx`. Si el cliente enviaba una contraseña o un token con un tipo
  inválido, el valor podía reaparecer en la respuesta. Ahora
  `app/main.py::_detalles_validacion` conserva solo `loc`, `msg` y `type`.
- **500**: `app/main.py::error_interno_handler` devuelve un mensaje genérico y
  registra el traceback solo en el log del servidor.
- **401/403/404/409**: los mensajes son de dominio y no incluyen el token ni la
  contraseña recibidos.

Prueba:
`tests/test_seguridad.py::test_validacion_no_ecoa_la_password_en_la_respuesta`.

## 3. Logs

| Archivo | Qué registra | Riesgo |
|---|---|---|
| `app/main.py` | Método, ruta y traceback de errores no controlados | No registra cuerpos ni cabeceras |
| `app/application/services/auth_service.py` | ID de usuario al detectar reutilización de refresh | No registra el token |
| `app/infrastructure/security/correo.py` | Aviso de SMTP no configurado o fallo de envío | No registra el enlace ni el token |
| `app/infrastructure/seeders/seed.py` | Usuarios demo y aviso de credenciales en README | Ya no imprime la contraseña demo |

Pruebas:
`tests/test_seguridad.py::test_login_fallido_no_registra_la_password_en_logs` y
`tests/test_seguridad.py::test_recuperacion_no_registra_el_token_en_logs`.

## 4. Configuración y repositorio

- `.env` está en `.gitignore`; `.env.example` solo contiene marcadores.
- `SECRET_KEY` tiene un valor de desarrollo, pero la aplicación **falla al
  iniciar** si `ENTORNO=produccion` y no se definió una clave propia.
- `compose.yaml` usa credenciales locales de PostgreSQL (`reservas/reservas`) y
  un `SECRET_KEY` de ejemplo. Son valores de desarrollo, no secretos reales;
  en un entorno expuesto deben reemplazarse por variables/secretos.
- `docs/diagrama-datos.md` y `docs/diagrama-clases.md` mencionan
  `password_hash` como **columna del esquema**, no como un hash real.
- `README.md` y `tests_manual/*.http` incluyen la contraseña de las cuentas
  demo. Son credenciales de prueba deliberadas para la evaluación, no datos de
  usuarios reales. Las capturas de evidencias deben ocultar tokens y enlaces.

## 5. Verificación rápida

```bash
# 1. Pruebas específicas
pytest tests/test_seguridad.py -q

# 2. Búsqueda de valores sensibles en el código propio
rg -n "password_hash|refresh_token|access_token|SECRET_KEY|SMTP_PASSWORD" app

# 3. Confirmar que .env no está versionado
git ls-files | rg "(^|/)\.env$"
```

El último comando no debe devolver archivos. Si se necesita una revisión
manual de capturas, ocultar cualquier `Authorization: Bearer ...`, token de
recuperación o contraseña antes de adjuntarlas.
