# Guion de defensa (10 minutos + 5 de preguntas)

> La defensa vale el **60 %** de la Entrega III. El grupo sortea al presentador,
> así que **los cuatro deben poder explicar cualquier sección**. Este guion está
> dividido en bloques de ~1 minuto para que se pueda repartir o presentar completo.

## Antes de entrar

```bash
docker compose up --build        # deja el stack listo
# verificar:
#   http://localhost:8000/docs   -> Swagger
#   http://localhost:8080        -> Adminer
#   http://localhost:8025        -> Mailpit
```

Checklist de 60 segundos:

- [ ] La API responde `GET /` con `{"estado": "operativo"}`.
- [ ] `admin@uct.cl` / `Demo.2026.Segura!` inicia sesión.
- [ ] Swagger muestra **31 operaciones**.
- [ ] Una pestaña con Mailpit abierta.
- [ ] Una pestaña con Adminer conectada a `db` (usuario `reservas`).
- [ ] `docs/diagrama-datos.md` y `docs/diagrama-clases.md` abiertos en GitHub.

---

## Bloque 1 — Problemática y alcance (1 min)

> «Los estudiantes y docentes reservan salas por WhatsApp, planillas o
> presencialmente. Eso produce choques de horario y tiempo perdido. Nuestra API
> administra usuarios, salas, equipamiento y reservas, y responde una pregunta
> concreta: **¿está libre esta sala en este horario?**
>
> El alcance está en el README: 31 operaciones, cinco reglas de negocio, cuatro
> entidades con relación 1:N y autenticación con dos perfiles. Lo que **no**
> hace: frontend, pagos y notificaciones automáticas fuera de la recuperación
> de contraseña.»

**Mostrar:** README, sección 4 (tabla de endpoints).

## Bloque 2 — Arquitectura por capas (1 min)

> «Seguimos arquitectura por capas. El dominio no conoce FastAPI ni SQLAlchemy:
> son dataclasses y funciones puras, y por eso se prueban sin base de datos.
> La aplicación orquesta casos de uso. La infraestructura implementa
> repositorios, modelos ORM y mappers. La presentación son los routers y DTOs.
> La dependencia siempre apunta hacia el dominio.»

**Mostrar:** `docs/diagrama-clases.md`, luego abrir
`app/domain/reglas_negocio.py` y `app/application/services/reserva_service.py`.

## Bloque 3 — Modelo de datos y migraciones (1 min)

> «Cuatro tablas de negocio y dos de seguridad. Usuario 1:N Reserva, Sala 1:N
> Reserva y Sala 1:N Equipamiento. El correo es único, el hash del refresh es
> único y el `jti` de recuperación es único. Todo está versionado con Alembic:
> dos migraciones, `upgrade head` y `downgrade` funcionan.»

**Mostrar:** `docs/diagrama-datos.md` y ejecutar en vivo:

```bash
alembic current
alembic history
```

## Bloque 4 — Demo: corrección del 500 (1,5 min)

> «En la entrega anterior, 10 endpoints devolvían 500 porque la entidad no
> declaraba tres campos. Ya está corregido y hay una prueba de regresión.»

1. `GET /reservas` → **200** con `proposito` y `num_asistentes`.
2. `GET /equipamientos` → **200**.
3. `pytest -q tests/test_integracion_reservas.py -k regresion` → 1 passed.

**Frase clave:** «El error no era de base de datos: era el constructor del
`dataclass`. Lo demuestra la prueba de regresión.»

## Bloque 5 — Demo: reglas de negocio (1,5 min)

Con token de administrador en Swagger (`Authorize`):

1. `PATCH /equipamientos/1/estado` → `{"estado": "danado"}`.
2. Crear una reserva en la sala 1 → **201**.
3. `PATCH /reservas/{id}/confirmar` → **400** «equipamiento dañado».
4. Restaurar el equipo a `disponible` y confirmar → **200**.

> «La regla existía pero no se invocaba. Ahora se ejecuta antes de confirmar.
> Además agregamos capacidad y sala en mantenimiento: cinco reglas activas.»

## Bloque 6 — Demo: autenticación y recuperación (2 min)

1. `POST /auth/login` con `admin@uct.cl` → access + refresh.
2. `GET /auth/me` con el Bearer → perfil.
3. `POST /auth/refresh` → par nuevo. **Repetir el refresh viejo → 401** y se
   cierran todas las sesiones.
4. `POST /auth/recuperacion/solicitar` con `luis@uct.cl`.
5. Abrir **Mailpit**, mostrar el correo y el enlace.
6. `POST /auth/recuperacion/restablecer` → 200. Repetir el mismo token → 401.
7. Iniciar sesión con la contraseña nueva → 200.

> «El refresh es opaco: en la base solo está su SHA-256. El enlace de
> recuperación es un JWT con propósito exclusivo y un `jti` de un solo uso.
> Al restablecer se invalidan todas las sesiones anteriores.»

## Bloque 7 — Contenedores, CI y pruebas (1 min)

> «`docker compose` levanta cuatro servicios: API, PostgreSQL, Adminer y
> Mailpit, con volumen persistente. El CI de GitHub Actions ejecuta Ruff,
> formato, 37 pruebas con 89 % de cobertura y el build de la imagen; si algo
> falla, el PR no se puede integrar.»

**Mostrar:** `compose.yaml`, pestaña **Actions** en GitHub, salida de `pytest`.

## Bloque 8 — Decisiones y limitaciones (1 min)

> «Tres decisiones que conviene explicar:
> 1. **Mailpit** en vez de SMTP real: la recuperación se demuestra sin
>    credenciales externas y el enlace también va en el JSON solo en dev.
> 2. **Refresh opaco con hash** en vez de JWT: si roban la base, no pueden
>    reutilizar sesiones.
> 3. **Kubero no fue solicitado** por el docente en esta sección; dejamos el
>    proyecto dockerizado, que es el requisito real de portabilidad.
>
> Limitación honesta: no hay frontend ni cobertura del 100 %; las ramas sin
> cubrir son fallos de infraestructura (SMTP caído, token expirado).»

---

## Preguntas probables y respuestas cortas

**¿Por qué Argon2id y no SHA-256?**
Porque SHA-256 es rápido y permite miles de millones de intentos por segundo.
Argon2id consume 64 MB y 3 iteraciones por intento, lo que encarece la fuerza
bruta. Además incorpora sal aleatoria por contraseña.

**¿Por qué el refresh no es un JWT?**
Porque un JWT no se puede revocar sin consultar una lista. Un token opaco
aleatorio se guarda como hash y se revoca con un `UPDATE`, lo que habilita
rotación y logout real.

**¿Qué pasa si roban un refresh y lo reutilizan?**
El token robado ya fue rotado; al reutilizarlo el sistema detecta la
reutilización y revoca **todas** las sesiones del usuario.

**¿Cómo garantizan que el enlace de recuperación se use una sola vez?**
El JWT lleva un `jti` que se registra en `recuperacion_tokens`. Al usarlo se
marca `usado=true`; un segundo intento responde 401.

**¿Por qué 401 y no 403 cuando falta el token?**
401 significa «no sé quién eres». 403 significa «sé quién eres, pero no puedes».
La matriz está en `test_e2e_matriz_de_permisos_401_403_200`.

**¿Por qué el estudiante no puede reservar a nombre de otro?**
El router sobrescribe `usuario_id` con el del token si el rol no es
administrador. Es una defensa contra la suplantación.

**¿Qué pasa si dos personas reservan el mismo horario a la vez?**
La regla de solapamiento se evalúa contra las reservas confirmadas. En SQLite
la escritura es serializada; en PostgreSQL el siguiente paso sería una
restricción de exclusión con rango de fechas, que está anotada como mejora.

**¿Cómo prueban que no volvió el 500?**
`test_regresion_reservas_y_equipamientos_ya_no_responden_500` recorre los
endpoints y valida los campos que antes rompían el constructor.

**¿Por qué SQLite en local y PostgreSQL en Docker?**
SQLite permite arrancar sin instalar nada; PostgreSQL cumple el requisito de
separar API y base de datos. SQLAlchemy y Alembic hacen el cambio transparente.

**¿Qué falta para producción?**
HTTPS, rotación de `SECRET_KEY`, límite de intentos por IP, cola de correo y
respaldos automáticos. Está en «Decisiones y limitaciones» del README.

---

## Reparto sugerido (si no sortean)

| Bloque | Responsable natural |
|---|---|
| 1 y 8 | Alonso (coordinación y documentación) |
| 2 y 3 | Diego (dominio y datos) |
| 4 y 5 | Jesús (API y reglas) |
| 6 | Alonso / Jesús |
| 7 | Tomás (calidad y pruebas) |

**Regla de oro:** nadie dice «eso lo hizo otro». Todos leen el bloque que no les
toca y ensayan una respuesta de 30 segundos.
