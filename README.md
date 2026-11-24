# Sistema de Reservas de Salas y Laboratorios — Grupo 06

API REST para reservar salas de estudio y laboratorios, con autenticación JWT,
roles, reglas de negocio, persistencia versionada y stack contenerizado.

**Curso:** Desarrollo de Backend (ICINF1108) · **Grupo:** 06
**Integrantes:** Alonso Lantaño, Tomás Mardones, Jesús Huentemil, Diego Vásquez

| | |
|---|---|
| **API (Swagger)** | http://localhost:8000/docs |
| **OpenAPI JSON** | http://localhost:8000/openapi.json |
| **Adminer (visor BD)** | http://localhost:8080 |
| **Mailpit (correo de prueba)** | http://localhost:8025 |

---

## 1. Stack

- **Python 3.12** + **FastAPI** + **Pydantic v2** + **Uvicorn**
- **SQLAlchemy 2** + **Alembic** (migraciones y seeders)
- **SQLite** en local / **PostgreSQL 16** en Docker
- **Argon2id** para contraseñas y **JWT (HS256)** para tokens
- **pytest** + **pytest-cov** (37 pruebas, 89 % de cobertura)
- **Ruff** (linter y formato) + **GitHub Actions** (CI)
- **Docker Compose**: API + PostgreSQL + Adminer + Mailpit

## 2. Inicio rápido en local

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements-dev.txt

cp .env.example .env          # ajustar SECRET_KEY
alembic upgrade head          # crea/actualiza las tablas
python -m app.infrastructure.seeders.seed

uvicorn app.main:app --reload
```

### Usuarios de demostración

| Correo | Rol | Contraseña |
|---|---|---|
| `admin@uct.cl` | administrador | `Demo.2026.Segura!` |
| `ana@uct.cl` | docente | `Demo.2026.Segura!` |
| `luis@uct.cl` | estudiante | `Demo.2026.Segura!` |

> La contraseña cumple la política: 12+ caracteres, mayúscula, minúscula,
> dígito y símbolo.

## 3. Inicio con Docker (stack completo)

```bash
docker compose up --build
```

| Servicio | Contenedor | Puerto | Función |
|---|---|---|---|
| `api` | `reservas-api` | 8000 | FastAPI + Uvicorn (migra y siembra al iniciar) |
| `db` | `reservas-db` | 5432 | PostgreSQL 16 con volumen `reservas-pgdata` |
| `adminer` | `reservas-adminer` | 8080 | Visor web de la base de datos |
| `mailpit` | `reservas-mailpit` | 1025 / 8025 | SMTP de prueba y buzón web |

El contenedor de la API ejecuta `alembic upgrade head` y el seeder antes de
levantar Uvicorn. El volumen `reservas-pgdata` conserva los datos entre
reinicios (se comprueba con `docker compose down` y `docker compose up`).

## 4. Endpoints (31 operaciones de negocio)

### Autenticación

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/auth/registro` | público | Crea cuenta de estudiante (no permite escalar rol) |
| POST | `/auth/login` | público | Devuelve access token + refresh token |
| POST | `/auth/refresh` | refresh token | Rota el refresh y emite un par nuevo |
| POST | `/auth/logout` | refresh token | Revoca el refresh indicado |
| GET | `/auth/me` | autenticado | Perfil del usuario del token |
| POST | `/auth/recuperacion/solicitar` | público | Genera enlace de un solo uso |
| POST | `/auth/recuperacion/restablecer` | token de recuperación | Cambia la contraseña e invalida sesiones |

### Salas

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/salas` | administrador | Crea una sala |
| GET | `/salas` | público | Lista con filtro, orden y paginación |
| GET | `/salas/{id}` | público | Sala + su equipamiento |
| GET | `/salas/{id}/equipamientos` | público | Equipamiento de la sala |
| GET | `/salas/{id}/disponibilidad` | público | Disponibilidad en un rango horario |
| PUT | `/salas/{id}` | administrador | Actualiza nombre, capacidad y ubicación |
| PATCH | `/salas/{id}/estado` | administrador | Disponible ↔ mantenimiento |
| DELETE | `/salas/{id}` | administrador | Elimina (409 si tiene reservas) |

### Usuarios

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/usuarios` | administrador | Crea usuario con rol y contraseña |
| GET | `/usuarios` | administrador | Lista usuarios |
| GET | `/usuarios/{id}` | propio usuario o administrador | Detalle |
| PATCH | `/usuarios/{id}/rol` | administrador | Cambia el rol |

### Equipamiento

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/equipamientos` | administrador | Crea equipo asociado a una sala |
| GET | `/equipamientos` | público | Lista (filtro `sala_id`) |
| GET | `/equipamientos/{id}` | público | Detalle |
| PATCH | `/equipamientos/{id}/estado` | administrador | Disponible ↔ dañado |
| DELETE | `/equipamientos/{id}` | administrador | Elimina |

### Reservas

| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/reservas` | autenticado | Crea reserva (a nombre propio si no es admin) |
| GET | `/reservas` | público | Filtros `usuario_id`, `sala_id`, `estado`, `fecha`; orden y paginación |
| GET | `/reservas/{id}` | público | Detalle |
| PUT | `/reservas/{id}` | dueño o administrador | Actualiza (conserva estado) |
| PATCH | `/reservas/{id}/confirmar` | dueño o administrador | Confirma si no hay conflicto ni equipos dañados |
| PATCH | `/reservas/{id}/cancelar` | dueño o administrador | Cancela (409 si ya estaba cancelada) |
| DELETE | `/reservas/{id}` | dueño o administrador | Elimina |

## 5. Autenticación y seguridad

```http
POST /auth/login
Content-Type: application/json

{"correo": "admin@uct.cl", "password": "Demo.2026.Segura!"}
```

```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "fpGuR7QPmMl-csWE...",
  "token_type": "bearer",
  "expires_in": 900
}
```

```http
GET /auth/me
Authorization: Bearer <access_token>
```

| Control | Implementación |
|---|---|
| Hash de contraseña | **Argon2id** (`time_cost=3`, 64 MB, paralelismo 4) |
| Política de contraseña | mínimo **12** caracteres + mayúscula + minúscula + dígito + símbolo |
| Token de acceso | JWT HS256, 15 minutos, con `sub`, `rol`, `tipo`, `jti`, `iat`, `exp` |
| Refresh token | **opaco** de 256 bits; en BD solo su **SHA-256** |
| Rotación | cada refresh revoca el anterior |
| Reutilización detectada | se revocan **todas** las sesiones del usuario |
| Logout | revoca el refresh (idempotente) |
| Recuperación | JWT con `tipo=recuperacion`, `jti` registrado, **un solo uso**, 15 min |
| Sesiones previas | se invalidan al restablecer la contraseña |
| Bloqueo | 5 intentos fallidos → cuenta bloqueada 15 minutos |
| 401 vs 403 | 401 sin token/inválido · 403 autenticado sin permiso o cuenta bloqueada |
| Perfiles | `administrador` y `usuario` (docente/estudiante) |

### Recuperación de contraseña en desarrollo

1. `POST /auth/recuperacion/solicitar` con `{"correo": "..."}`.
2. El correo se entrega a **Mailpit** (`http://localhost:8025`).
3. En `ENTORNO=dev` el enlace también se devuelve en `enlace_recuperacion`
   (la pauta lo permite en entornos de prueba). En `produccion` se oculta.
4. `POST /auth/recuperacion/restablecer` con `{"token": "...", "password_nueva": "..."}`.

## 6. Reglas de negocio

| # | Regla | Respuesta |
|---|---|---|
| 1 | Una reserva no puede terminar antes de empezar | `400` |
| 2 | No se reserva una sala con otra reserva **confirmada** solapada | `409` |
| 3 | No se confirma una reserva si la sala tiene **equipamiento dañado** | `400` |
| 4 | Los asistentes no pueden superar la **capacidad** de la sala | `400` |
| 5 | No se reserva una sala en **mantenimiento** | `409` |

## 7. Formato uniforme de error

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "No existe una sala con ID 999.",
    "details": []
  }
}
```

| Código | HTTP | Cuándo |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Tipos o campos inválidos (Pydantic) |
| `RESOURCE_NOT_FOUND` | 404 | El recurso no existe |
| `CONFLICT` | 409 | Solapamiento, sala en mantenimiento, borrado con dependencias |
| `BUSINESS_RULE_VIOLATION` | 400 | Capacidad, fechas, equipamiento dañado, contraseña débil |
| `UNAUTHORIZED` | 401 | Token ausente, inválido o expirado |
| `FORBIDDEN` | 403 | Rol insuficiente o recurso ajeno |
| `ACCOUNT_LOCKED` | 403 | Bloqueo por intentos fallidos |
| `INTERNAL_ERROR` | 500 | Excepción no controlada (siempre JSON, nunca texto plano) |

## 8. Pruebas y calidad

```bash
pytest --cov=app --cov-report=term-missing
ruff check .
ruff format --check .
```

| Tipo | Cantidad | Archivo |
|---|---|---|
| Unitarias (dominio y contraseñas) | 7 | `tests/test_unit_reglas.py` |
| Integración (auth, reservas, salas) | 27 | `tests/test_integracion_auth.py`, `tests/test_integracion_reservas.py` |
| End-to-end | 3 | `tests/test_e2e.py` |

Resultado actual: **37 pruebas aprobadas, 89 % de cobertura**.
El CI (`.github/workflows/ci.yml`) ejecuta linter, formato, pruebas con
`--cov-fail-under=85` y build de la imagen Docker en cada push y PR.

## 9. Estructura del proyecto

```
app/
├── domain/                 # Entidades, errores y reglas de negocio (sin framework)
├── application/services/   # Casos de uso: auth, reservas, salas, usuarios, equipos
├── infrastructure/
│   ├── models/             # Modelos ORM
│   ├── mappers/            # Entidad ↔ modelo
│   ├── repositories/       # Acceso a datos
│   ├── security/           # Argon2id, JWT, correo
│   ├── config.py           # Configuración por variables de entorno
│   └── seeders/            # Datos de demostración
└── presentation/
    ├── routers/            # Endpoints FastAPI
    ├── schemas/dtos.py     # DTOs de entrada/salida
    └── dependencies.py     # Sesión de BD y usuario autenticado
migrations/                 # Alembic
tests/                      # pytest
docs/                       # Diagramas y retroalimentación
tests_manual/               # Colecciones .http e informe de evidencias
```

## 10. Documentación

- [Diagrama de datos](docs/diagrama-datos.md)
- [Diagrama de clases](docs/diagrama-clases.md)
- [Matriz de retroalimentación](docs/retroalimentacion.md)
- [Guion de defensa](docs/guia-defensa.md)
- [Informe de pruebas de la Entrega III](tests_manual/informe_pruebas_entrega3.md)

## 11. Decisiones y limitaciones

- **Sin frontend:** la pauta no lo solicita; la comprobación se hace con Swagger.
- **Correo:** se usa **Mailpit** en lugar de un SMTP real para que la
  recuperación sea demostrable y reproducible sin credenciales externas.
- **Despliegue en Kubero:** no fue solicitado por el docente en esta sección;
  el proyecto queda contenerizado y listo para cualquier PaaS. Se documenta la
  decisión para que no se interprete como un requisito omitido.
- **Recuperación en producción:** `EXPONER_ENLACE_RECUPERACION=false` evita que
  el enlace se filtre en la respuesta JSON.

## 12. Historial de versiones

- **v1.0** — Entrega III: correcciones de la retroalimentación, autenticación
  completa, recuperación de contraseña, contenedores, CI y pruebas automatizadas.
