# Alonso Lantaño

**Rol:** coordinación, despliegue y documentación.

## Aportes en la Entrega III

- Dockerfile y `compose.yaml` con API, PostgreSQL 16, Adminer y Mailpit.
- Integración continua en GitHub Actions: Ruff, pruebas con cobertura y build de la imagen.
- Configuración de calidad del proyecto (`pyproject.toml`, `.gitignore` y dependencias de desarrollo).
- README con instalación, credenciales demo, endpoints y estructura por capas.
- Matriz de retroalimentación y guía de defensa.

## Verificación

- `docker compose up --build` levanta los cuatro servicios.
- La API responde en `http://localhost:8000/docs`.
