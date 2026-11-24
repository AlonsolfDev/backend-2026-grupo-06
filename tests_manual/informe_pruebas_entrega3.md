# Informe de pruebas — Entrega III (versión 1.0)

**Proyecto:** API de Reservas de Salas y Laboratorios — Grupo 06
**Curso:** Desarrollo de Backend (ICINF1108)
**Código probado:** rama `fix/correcciones-entrega3`, tag `v1.0`
**Fecha de ejecución:** 22 de noviembre de 2026
**Entorno:** Python 3.12 / SQLite (pruebas) · PostgreSQL 16 (Docker)

> Este informe reemplaza al de la Entrega I–II, que describía un código anterior.
> Cada caso indica el resultado **observado** en esta versión. Las capturas se
> guardan en `tests_manual/capturas_entrega3/` con el nombre del caso.

---

## 1. Resultado general

| Suite | Casos | Resultado |
|---|---|---|
| Unitarias de dominio | 7 | ✅ 7 aprobadas |
| Integración de autenticación | 12 | ✅ 12 aprobadas |
| Integración de reservas, salas y equipamiento | 15 | ✅ 15 aprobadas |
| End-to-end | 3 | ✅ 3 aprobadas |
| **Total** | **37** | **✅ 37 aprobadas, 0 fallidas** |

```
$ pytest --cov=app --cov-report=term
37 passed
TOTAL  1075 statements  113 missed  89% coverage
```

Cobertura exigida: 85 %. **Cobertura obtenida: 89 %.**

---

## 2. Prueba de regresión del defecto reportado

**Observación del docente:** «solo 8 de 18 operaciones funcionan; los `TypeError`
escapan como 500 en texto plano».

| Paso | Antes | Ahora |
|---|---|---|
| `GET /reservas` | 500 texto plano | **200** con `proposito` y `num_asistentes` |
| `GET /reservas/1` | 500 texto plano | **200** |
| `GET /equipamientos` | 500 texto plano | **200** con `descripcion` |
| `POST /reservas` | 500 texto plano | **201** |
| `PATCH /reservas/1/confirmar` | 500 texto plano | **200** |

Prueba automatizada que lo cubre:
`tests/test_integracion_reservas.py::test_regresion_reservas_y_equipamientos_ya_no_responden_500`

**Causa raíz documentada:** `Reserva` no declaraba `proposito` ni
`num_asistentes`, y `Equipamiento` no declaraba `descripcion`, mientras los
mappers y modelos ORM sí los enviaban al constructor del `dataclass`.

---

## 3. Casos manuales (para capturar en Swagger o REST Client)

Servidor: `http://localhost:8000` · Swagger: `/docs`
Credenciales: `admin@uct.cl` / `Demo.2026.Segura!`

### Autenticación

| ID | Caso | Petición | Esperado | Observado |
|---|---|---|---|---|
| CP-01 | Login correcto | `POST /auth/login` admin | 200 + par de tokens | ✅ 200 |
| CP-02 | Login con contraseña incorrecta | `POST /auth/login` | 401 `UNAUTHORIZED` | ✅ 401 |
| CP-03 | Bloqueo por 5 intentos | 5 × `POST /auth/login` | 5.º → 403 `ACCOUNT_LOCKED` | ✅ 403 |
| CP-04 | Perfil sin token | `GET /auth/me` | 401 + `WWW-Authenticate: Bearer` | ✅ 401 |
| CP-05 | Perfil con token | `GET /auth/me` admin | 200 | ✅ 200 |
| CP-06 | Registro público | `POST /auth/registro` | 201, rol estudiante | ✅ 201 |
| CP-07 | Contraseña débil | `POST /auth/registro` `"123456"` | 400 `BUSINESS_RULE_VIOLATION` | ✅ 400 |
| CP-08 | Refresh válido | `POST /auth/refresh` | 200 + token nuevo | ✅ 200 |
| CP-09 | Refresh reutilizado | repetir el refresh anterior | 401 y cierre de sesiones | ✅ 401 |
| CP-10 | Logout | `POST /auth/logout` | 204 | ✅ 204 |
| CP-11 | Refresh tras logout | `POST /auth/refresh` | 401 | ✅ 401 |
| CP-12 | Solicitud de recuperación | `POST /auth/recuperacion/solicitar` | 202 + enlace en dev | ✅ 202 |
| CP-13 | Enlace en Mailpit | abrir `http://localhost:8025` | correo con enlace | ✅ recibido |
| CP-14 | Restablecer contraseña | `POST /auth/recuperacion/restablecer` | 200 | ✅ 200 |
| CP-15 | Enlace usado dos veces | repetir el mismo token | 401 «ya fue utilizado» | ✅ 401 |
| CP-16 | Login con contraseña nueva | `POST /auth/login` | 200 | ✅ 200 |

### Autorización (401 frente a 403)

| ID | Caso | Petición | Esperado | Observado |
|---|---|---|---|---|
| CP-17 | Crear sala sin token | `POST /salas` | 401 | ✅ 401 |
| CP-18 | Crear sala como estudiante | `POST /salas` con token estudiante | 403 | ✅ 403 |
| CP-19 | Crear sala como administrador | `POST /salas` con token admin | 201 | ✅ 201 |
| CP-20 | Listar usuarios como docente | `GET /usuarios` | 403 | ✅ 403 |
| CP-21 | Reserva ajena | `PATCH /reservas/{id}/cancelar` con otra cuenta | 403 | ✅ 403 |

### Salas, equipamiento y reservas

| ID | Caso | Petición | Esperado | Observado |
|---|---|---|---|---|
| CP-22 | Listar salas con filtro/orden/página | `GET /salas?estado=disponible&ordenar_por=capacidad&direccion=desc` | 200 paginado | ✅ 200 |
| CP-23 | Sala con equipamiento | `GET /salas/1` | 200 + `equipamientos[]` | ✅ 200 |
| CP-24 | Disponibilidad libre | `GET /salas/2/disponibilidad` | `disponible: true` | ✅ 200 |
| CP-25 | Disponibilidad ocupada | `GET /salas/1/disponibilidad` | `disponible: false` | ✅ 200 |
| CP-26 | Crear reserva | `POST /reservas` | 201 `pendiente` | ✅ 201 |
| CP-27 | Reserva que excede capacidad | `POST /reservas` `num_asistentes: 99` | 400 | ✅ 400 |
| CP-28 | Solapamiento con confirmada | `POST /reservas` horario ocupado | 409 | ✅ 409 |
| CP-29 | Confirmar reserva | `PATCH /reservas/{id}/confirmar` | 200 `confirmada` | ✅ 200 |
| CP-30 | Equipo dañado impide confirmar | marcar `danado` y confirmar | 400 «dañado» | ✅ 400 |
| CP-31 | Reparar y confirmar | estado `disponible` y confirmar | 200 | ✅ 200 |
| CP-32 | Cancelar reserva | `PATCH /reservas/{id}/cancelar` | 200 `cancelada` | ✅ 200 |
| CP-33 | Cancelar dos veces | repetir | 409 | ✅ 409 |
| CP-34 | Sala en mantenimiento | `PATCH /salas/{id}/estado` y reservar | 409 | ✅ 409 |
| CP-35 | Eliminar sala con reservas | `DELETE /salas/1` | 409 | ✅ 409 |
| CP-36 | Recurso inexistente | `GET /salas/9999` | 404 `RESOURCE_NOT_FOUND` | ✅ 404 |
| CP-37 | Dato inválido | `POST /salas` capacidad 0 | 422 `VALIDATION_ERROR` | ✅ 422 |

### Persistencia

| ID | Caso | Procedimiento | Esperado | Observado |
|---|---|---|---|---|
| CP-38 | Persistencia tras reinicio | crear reserva, `docker compose restart api`, `GET /reservas` | la reserva sigue | ✅ |
| CP-39 | Volumen de PostgreSQL | `docker compose down`, `up`, `GET /reservas` | datos conservados | ✅ |
| CP-40 | Visor de base de datos | Adminer `http://localhost:8080` | tablas y filas visibles | ✅ |

---

## 4. Cómo reproducir

```bash
# Pruebas automatizadas
pytest --cov=app --cov-report=term-missing

# Calidad
ruff check .
ruff format --check .

# Stack completo
docker compose up --build

# Migraciones
alembic current      # a1b2c3d4e5f6 (head)
alembic history      # 2 revisiones
```

Las colecciones `.http` de esta carpeta se ejecutan de arriba hacia abajo en
VS Code (REST Client) y cubren los casos CP-01 a CP-37.

### Validación del stack Docker

El stack se levantó y verificó el **23-11-2026** con Docker 29.8.2 y Compose
v5.5.1 sobre Windows. Resultado:

- `docker compose up -d --build`: 4 contenedores; `db` y `mailpit` en estado
  `healthy`, `api` respondiendo en `http://localhost:8000`.
- Migraciones aplicadas: `e4571a0ef542` → `a1b2c3d4e5f6` (head).
- Seeder ejecutado con los tres usuarios demo.
- `GET /` 200, `GET /reservas` 200 (2 reservas), `GET /equipamientos` 200 (2 equipos).
- `POST /auth/login` 200 (`expires_in` 900) y `GET /auth/me` 200.
- `POST /auth/recuperacion/solicitar` 202, correo visible en Mailpit (8025).
- Enlace de recuperación: primer uso 200, segundo uso 401, contraseña anterior
  rechazada y contraseña nueva aceptada.
- Rol insuficiente: 403. Sin token: 401.
- Adminer (8080) y Mailpit (8025) responden 200.

---

## 5. Evidencia pendiente de captura

Las capturas deben regenerarse sobre **esta** versión. Lista mínima para la
entrega (12 imágenes):

1. `GET /` operativo.
2. Swagger con las 31 operaciones.
3. `GET /reservas` 200 (prueba del 500 corregido).
4. `GET /equipamientos` 200.
5. Login 200 con tokens.
6. `GET /auth/me` 200.
7. Refresh reutilizado 401.
8. Correo de recuperación en Mailpit.
9. Enlace de recuperación usado dos veces 401.
10. 403 por rol insuficiente.
11. Equipo dañado impidiendo confirmar (400).
12. Adminer mostrando las tablas.

Guardar en `tests_manual/capturas_entrega3/` con el número de caso en el nombre.
