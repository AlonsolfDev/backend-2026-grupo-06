# Jesús Huentemil

**Rol:** seguridad, API y reglas de negocio.

## Aportes en la Entrega III

- Hashing con Argon2id, política de contraseñas y tokens JWT.
- Registro, login, refresh con rotación, logout y recuperación de contraseña de un solo uso.
- DTOs, validaciones y contrato OpenAPI de los endpoints.
- Endpoints de salas con equipamiento, disponibilidad y equipamientos.
- Cinco reglas de negocio activas y autorización por dueño o administrador.
- Manejo global de excepciones con respuestas JSON uniformes (401/403/500).

## CÃ³mo lo explico en la defensa

- Recorrido del login: DTO, router, `auth_service`, repositorio y seguridad.
- Diferencia entre 401 (sin token o token invÃ¡lido) y 403 (usuario vÃ¡lido sin permiso).
