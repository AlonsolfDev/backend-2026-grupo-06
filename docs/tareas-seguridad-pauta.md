# Ajustes de seguridad pendientes (pauta 5.5 y 5.6)

- [x] Configurar CORS con orígenes explícitos en `app/main.py`.
- [x] Limitar solicitudes repetidas de recuperación sin bloquear la cuenta.
- [x] Verificar que no aparezcan `password`, `password_hash`, tokens ni secretos en DTO, errores, evidencias ni logs.

## 1. CORS con orígenes explícitos

- `app/infrastructure/config.py` lee `CORS_ORIGINS` como una lista separada por
  coma. Por defecto solo incluye los puertos locales de desarrollo
  (`3000` y `5173`).
- `app/main.py` registra `CORSMiddleware` con `allow_credentials=True`,
  métodos y cabeceras explícitos. No se usa `*`.
- En producción se debe definir `CORS_ORIGINS` con el dominio real del
  frontend; el valor de ejemplo está en `.env.example` y `compose.yaml`.

## 2. Límite de solicitudes de recuperación

- `RECUPERACION_COOLDOWN_SEGUNDOS` (120 s por defecto) define la ventana
  mínima entre solicitudes de una misma cuenta.
- La segunda solicitud dentro de la ventana recibe el mismo `202` genérico,
  no crea otro `jti`, no reenvía correo y **no incrementa intentos fallidos ni
  bloquea la cuenta**.
- El control se apoya en `recuperacion_tokens.creado_en` y en
  `RecuperacionTokenRepository.obtener_ultimo_por_usuario`.
- La respuesta sigue siendo genérica para correos existentes e inexistentes,
  de modo que no se puede enumerar cuentas por el mensaje ni por el estado.

## 3. Revisión de secretos

El detalle archivo por archivo está en
[`docs/revision-secretos.md`](revision-secretos.md). Los cambios principales:

- El manejador de errores `422` ya no reenvía `input` ni `ctx` de Pydantic;
  solo conserva `loc`, `msg` y `type`. Así una contraseña o token enviado con
  un tipo inválido no se refleja en la respuesta.
- Los DTO de salida (`UsuarioOut`, `SalaOut`, etc.) no declaran
  `password_hash`.
- Los logs de autenticación solo usan el ID del usuario; no registran
  contraseñas, hashes, tokens ni enlaces de recuperación.
- `.env` está excluido por `.gitignore`; `.env.example` solo contiene
  marcadores. Las credenciales demo del README son cuentas de prueba
  deliberadas y no datos reales.

## 4. Verificación

```bash
# Suite completa con cobertura
pytest --cov=app --cov-report=term-missing --cov-fail-under=85

# Linter y formato
ruff check .
ruff format --check .

# Pruebas específicas de estos ajustes
pytest tests/test_seguridad.py -q
```

Resultado esperado: **44 pruebas aprobadas** y cobertura **≥ 85 %**. Las
pruebas de `tests/test_seguridad.py` cubren CORS permitido/denegado, el límite
de recuperación sin bloqueo, la no exposición de `password_hash`, la no
devolución de valores sensibles en errores `422` y la ausencia de contraseñas
y tokens en los logs.
