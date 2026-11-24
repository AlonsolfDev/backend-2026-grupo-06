# Matriz de retroalimentación — Entrega III

Este documento responde, punto por punto, a la retroalimentación recibida en la
Entrega I–II. Cada observación se vincula con el cambio realizado, el commit que
lo contiene y la evidencia que permite verificarlo.

Los hashes citados corresponden a los commits de la rama
`fix/correcciones-entrega3`, integrada a `main` mediante el pull request de la
Entrega III.

**Puntaje de referencia:** 18/30 en código (nota 4,6) y 13/24 en defensa (nota 4,3).
Las observaciones se agrupan en 5 causas técnicas y 4 de evidencia.

---

## 1. Observaciones del docente y su corrección

### O1. «La API inicia y registra 18 operaciones, pero solo 8 funcionan»

**Causa raíz:** la entidad de dominio `Reserva` no declaraba `proposito` ni
`num_asistentes`, y `Equipamiento` no declaraba `descripcion`. Los mappers y los
modelos ORM sí enviaban esos campos, por lo que el constructor del `dataclass`
lanzaba `TypeError` y los 10 endpoints de reservas y equipamiento respondían
**500 en texto plano**.

| Cambio | Archivo | Commit | Evidencia |
|---|---|---|---|
| Declarar los 3 campos faltantes y las entidades de seguridad | `app/domain/entities.py` | `1b4c902` (`fix(dominio): completa Reserva, Equipamiento y Usuario`) | `tests/test_integracion_reservas.py::test_regresion_reservas_y_equipamientos_ya_no_responden_500` |
| Alinear mapper y modelo de usuario con las credenciales | `app/infrastructure/mappers/usuario_mapper.py`, `app/infrastructure/models/usuario_model.py` | `1b4c902` | suite de integración |

**Antes:** `GET /reservas` → `500 Internal Server Error` (texto plano).
**Después:** `GET /reservas` → `200` con `proposito` y `num_asistentes`.
Los 18 endpoints originales responden y se agregaron 13 operaciones nuevas: 31
de negocio en total (32 contando `GET /` de salud).

---

### O2. «El archivo de diagrama está vacío»

`docs/diagrama-datos.md` pesaba **0 bytes**.

| Cambio | Archivo | Commit |
|---|---|---|
| Diagrama entidad-relación en Mermaid, con cardinalidades, índices y migraciones | `docs/diagrama-datos.md` | `2ea6f14` (`docs(datos): diagrama de datos en Mermaid`) |
| Diagrama de clases por capas y flujo de una petición | `docs/diagrama-clases.md` | `25359ed` (`docs(datos): diagrama de clases por capas`) |

Ambos diagramas se renderizan directamente en GitHub y en la defensa.

---

### O3. «La regla de equipamiento dañado no se invoca»

La función `validar_equipamiento_disponible` existía en
`app/domain/reglas_negocio.py` pero **no se llamaba desde ningún caso de uso**.

| Cambio | Archivo | Commit | Evidencia |
|---|---|---|---|
| Invocar la regla al confirmar una reserva | `app/application/services/reserva_service.py` | `a761e10` (`feat(negocio): cinco reglas activas y reservas completas`) | `test_equipamiento_danado_impide_confirmar` (400) |
| Agregar regla de capacidad y de sala en mantenimiento | `app/domain/reglas_negocio.py` | `a761e10` | `test_capacidad_excedida_lanza_regla_negocio`, `test_sala_en_mantenimiento_no_es_reservable` |

Se pasó de **2 reglas invocadas** a **5 reglas de negocio activas**:

1. Fechas coherentes.
2. Sin solapamiento con reservas confirmadas.
3. Sin equipamiento dañado al confirmar.
4. Capacidad de la sala.
5. Sala no puede estar en mantenimiento.

---

### O4. «Los `TypeError` escapan como 500 en texto plano»

`app/main.py` manejaba errores de dominio y `ValueError`, pero no tenía un
respaldo para excepciones inesperadas.

| Cambio | Archivo | Commit | Evidencia |
|---|---|---|---|
| Manejador global de `Exception` con log y respuesta JSON uniforme | `app/main.py` | `f4f92d1` (`fix(errores): manejador global de excepciones y errores 401/403`) | `INTERNAL_ERROR` documentado en README y OpenAPI |
| Jerarquía de errores 401/403/409/400 | `app/domain/errores.py` | `e4e47ea` (`feat(auth): registro, login, refresh rotado, logout y perfil`) | `test_me_sin_token_responde_401`, `test_e2e_matriz_de_permisos_401_403_200` |

Ninguna excepción no controlada vuelve a salir como texto plano: siempre se
responde `{"error": {"code": "INTERNAL_ERROR", ...}}` y se registra el traceback
en el log del servidor (nunca en la respuesta).

---

### O5. «La evidencia no está actualizada con el código entregado»

| Cambio | Archivo | Commit |
|---|---|---|
| Nuevo informe de pruebas con resultados de la versión actual | `tests_manual/informe_pruebas_entrega3.md` | `a152ad4` (`docs(pruebas): informe de evidencias y colecciones http`) |
| Colecciones `.http` actualizadas con login y endpoints nuevos | `tests_manual/*.http` | `a152ad4` |
| Suite automatizada reproducible (37 pruebas) | `tests/` | `bd56e47`, `8e2fe48`, `8b294a1`, `caa14d8` |

Las capturas del informe anterior se conservan como histórico; el informe nuevo
indica qué captura corresponde a cada caso y con qué comando se reproduce.

---

### O6. «Más de 5 endpoints incumplen el contrato REST/DTO/OpenAPI»

| Cambio | Archivo | Commit |
|---|---|---|
| DTOs con ejemplos, validaciones y descripciones en cada campo | `app/presentation/schemas/dtos.py` | `b7ae618` (`feat(api): DTOs y contrato OpenAPI completo`) |
| Respuestas `401/403/404/409` declaradas en OpenAPI | `app/presentation/routers/*.py` | `b7ae618`, `d1e9ac8` |
| Endpoints del P5 que faltaban (disponibilidad, cancelar, filtro por usuario/fecha/estado, sala con equipamiento) | routers + services | `d1e9ac8` (`feat(api): salas con equipamiento y consulta de disponibilidad`), `a761e10` |

OpenAPI documenta ahora **31 operaciones**, con ejemplos de request/response y
códigos de error por endpoint.

---

### O7. «Falta autenticación, recuperación de contraseña, contenedores, CI y pruebas»

Estos puntos no estaban en la pauta de la Entrega I–II, pero sí en la III.

| Requisito | Implementación | Commit | Evidencia |
|---|---|---|---|
| Registro y login | `POST /auth/registro`, `POST /auth/login` | `e4e47ea` | `tests/test_integracion_auth.py` |
| Argon2id + contraseña de 12+ | `app/infrastructure/security/passwords.py` | `a97b693` (`feat(seguridad): Argon2id, JWT y refresh token opaco`) | `test_politica_de_password_y_hash_argon2id` |
| Access JWT + refresh opaco con hash | `app/infrastructure/security/tokens.py` | `a97b693` | `test_refresh_rota_el_token_y_detecta_reutilizacion` |
| Rotación y revocación | `POST /auth/refresh`, `POST /auth/logout` | `e4e47ea` | reutilización → 401 y cierre global |
| Recuperación con `jti` de un solo uso | `POST /auth/recuperacion/*` | `e4e47ea`, `2224ccf` | `test_recuperacion_enlace_de_un_solo_uso` |
| Invalidación de sesiones previas | `auth_service.restablecer_password` | `e4e47ea` | `test_restablecer_invalida_sesiones_previas` |
| 401 vs 403 y dos perfiles | `dependencies.get_current_user` / `require_admin` | `e4e47ea` | `test_e2e_matriz_de_permisos_401_403_200` |
| Dockerfile + compose con API, BD, visor y volumen | `Dockerfile`, `compose.yaml` | `74d9e73` (`build: Dockerfile, compose con PostgreSQL, Adminer y Mailpit`) | `docker compose up --build` |
| CI con linter, formato, pruebas y build | `.github/workflows/ci.yml` | `d14ab49` (`ci: workflow de lint, pruebas con cobertura y build`) | pestaña Actions |
| Pruebas 6+6+3 y cobertura 85 % | `tests/` | `bd56e47`, `8e2fe48`, `8b294a1`, `caa14d8` | 37 pruebas, 89 % |

---

## 2. Resumen de causas y criterios recuperados

| Causa | Criterios de la rúbrica que recupera |
|---|---|
| Campos faltantes en el dominio | 1. Ejecución y endpoints · 2. Modelo del dominio · 5. Validaciones · 6. Errores HTTP |
| Diagramas ausentes/vacíos | 2. Modelo del dominio |
| Regla no invocada | 5. Validaciones y reglas |
| Sin manejador global | 6. Respuestas y errores HTTP |
| Evidencia desactualizada | 10. Pruebas iniciales |
| Endpoints del P5 faltantes | 1. Ejecución · 3. REST/DTO/OpenAPI |
| Autenticación y recuperación | Criterios nuevos de la Entrega III |
| Contenedores y CI | Calidad, CI/CD y despliegue |

## 3. Verificación rápida para la defensa

```bash
# 1. La API responde y no hay 500
pytest -q
ruff check . && ruff format --check .

# 2. Los endpoints que antes fallaban
curl http://localhost:8000/reservas
curl http://localhost:8000/equipamientos

# 3. Regla de equipamiento dañado (requiere token de administrador)
curl -X PATCH http://localhost:8000/equipamientos/1/estado \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" -d '{"estado":"danado"}'
```

## 4. Limitaciones declaradas

- No hay frontend (fuera de alcance de la pauta).
- El correo usa Mailpit, no un SMTP productivo.
- Kubero no fue solicitado por el docente en esta sección; el proyecto queda
  dockerizado y portable.
- La cobertura es 89 %, no 100 %: las ramas sin cubrir son errores de
  infraestructura (SMTP caído, token expirado por reloj) y se documentan como
  tales.
