# Proyecto Backend - Grupo 6 (ICINF1108)

API REST para gestión de reservas de salas.

## Integrantes y responsabilidades

Jefe de grupo: Alonso Lantaño.

## Integrantes y Responsabilidades
| Integrante | Área de Responsabilidad | Trabajo realizado |
| --- | --- | --- |
| Alonso Lantaño | Coordinación + Documentación e Integración | Liderazgo, integración Git, README, contratos OpenAPI y docs |
| Diego Vásquez | Dominio y Datos | Modelos ORM, SQLite, migraciones Alembic y seeders |
| Jesús Huentemil | API y Lógica de Negocio | Routers FastAPI, servicios, excepciones y paginación |
| Tomás Mardones | Calidad y Pruebas | Matriz de pruebas, capturas de evidencias e informe |

## Entidades

| Entidad | Descripción |
|---|---|
| **Sala** | Espacio disponible para ser reservado |
| **Usuario** | Persona que realiza reservas |
| **Reserva** | Asocia un usuario con una sala. Al crearla se valida que la sala y el usuario existan |
| **Equipamiento** | Recursos disponibles, con un estado que puede actualizarse |

## Requisitos

- Python 3.14 (versión con la que se probó el proyecto)
- Git

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/AlonsolfDev/backend-2026-grupo-06.git
cd backend-2026-grupo-06
```
2. Crear y activar el entorno virtual:
```bash
python -m venv venv
# Windows (PowerShell): venv\Scripts\Activate.ps1
# Linux / Mac: source venv/bin/activate
```
3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Variables de entorno

Copiar `.env.example` a `.env` y ajustar si es necesario:
```
DATABASE_URL=sqlite:///./reservas.db
```

## Base de datos, migraciones y seeders

La base de datos usa SQLite por defecto (`sqlite:///./reservas.db`) y se configura con la variable `DATABASE_URL`. Los modelos ORM (SQLAlchemy) están en `app/infrastructure/models/` e incluyen las cuatro entidades con sus relaciones 1:N (Usuario→Reserva, Sala→Reserva, Sala→Equipamiento). El diagrama de datos está en `docs/diagrama-datos.md`.

Crear las tablas desde cero:

```bash
alembic upgrade head
```

Cargar datos de ejemplo (se puede ejecutar varias veces sin duplicar registros):

```bash
python -m app.infrastructure.seeders.seed
```

Para reiniciar la base: borrar `reservas.db` y repetir los dos comandos.

## Ejecución

```bash
uvicorn app.main:app --reload
```
El servidor queda disponible en http://127.0.0.1:8000

Documentación Swagger: http://127.0.0.1:8000/docs

## Arquitectura por capas

| Capa | Carpeta | Función |
|---|---|---|
| Presentación | `app/presentation/` | Routers HTTP y DTOs (schemas) |
| Aplicación | `app/application/services/` | Casos de uso y coordinación |
| Dominio | `app/domain/` | Entidades y reglas de negocio |
| Infraestructura | `app/infrastructure/` | Repositorios y acceso a datos |

`app/main.py` crea y ensambla la aplicación. La lógica de negocio no vive en los routers.

## Recorrido de una solicitud

El flujo técnico de una petición (por ejemplo, al registrar una reserva en `POST /reservas`) recorre las capas en la siguiente secuencia:

[ Cliente / Swagger UI ]
       │
       ▼ (1) Envío de JSON con datos
┌──────────────────────────────────────────────┐
│  Presentation (app/presentation/routers/)    │  <-- Valida formato con Pydantic (ReservaCreate DTO)
└──────────────────────┬───────────────────────┘
                       │
                       ▼ (2) Evaluación de lógica
┌──────────────────────────────────────────────┐
│  Application (app/application/services/)     │  <-- Aplica reglas (fechas válidas y disponib. de sala)
└──────────────────────┬───────────────────────┘
                       │
                       ▼ (3) Mapeo y persistencia
┌──────────────────────────────────────────────┐
│  Infrastructure (app/infrastructure/repos/)  │  <-- Traduce entidad a ORM SQLAlchemy (ReservaModel)
└──────────────────────┬───────────────────────┘
                       │
                       ▼ (4) Transacción SQL
┌──────────────────────────────────────────────┐
│  Base de Datos (reservas.db - SQLite)        │  <-- Guarda el registro persistente en disco
└──────────────────────────────────────────────┘

## Endpoints principales

### Salas

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/salas` | Crear una sala |
| GET | `/salas` | Listar todas las salas |
| GET | `/salas/{sala_id}` | Obtener una sala por ID |
| PUT | `/salas/{sala_id}` | Actualizar una sala |
| DELETE | `/salas/{sala_id}` | Eliminar una sala |

### Usuarios

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/usuarios` | Crear un usuario |
| GET | `/usuarios` | Listar todos los usuarios |
| GET | `/usuarios/{usuario_id}` | Obtener un usuario por ID |

### Reservas

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/reservas` | Crear una reserva (valida que existan la sala y el usuario) |
| GET | `/reservas` | Listar todas las reservas |
| GET | `/reservas/{reserva_id}` | Obtener una reserva por ID |
| PUT | `/reservas/{reserva_id}` | Actualizar una reserva |
| DELETE | `/reservas/{reserva_id}` | Eliminar una reserva |
| PATCH | `/reservas/{reserva_id}/confirmar` | Confirmar una reserva |

### Equipamientos

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/equipamientos` | Crear un equipamiento |
| GET | `/equipamientos` | Listar todos los equipamientos |
| GET | `/equipamientos/{equipamiento_id}` | Obtener un equipamiento por ID |
| PATCH | `/equipamientos/{equipamiento_id}/estado` | Actualizar el estado de un equipamiento |

## Estructura del proyecto

```
backend-2026-grupo-06/
├── app/
│   ├── main.py                      # Punto de entrada de la aplicación FastAPI
│   ├── presentation/
│   │   ├── routers/                 # Endpoints de la API
│   │   │   ├── sala_router.py
│   │   │   ├── usuario_router.py
│   │   │   ├── reserva_router.py
│   │   │   └── equipamiento_router.py
│   │   └── schemas/
│   │       └── dtos.py              # Modelos Pydantic de entrada y salida
│   ├── application/
│   │   └── services/                # Lógica de negocio (una por entidad)
│   │       ├── sala_service.py
│   │       ├── usuario_service.py
│   │       ├── reserva_service.py   # Valida que existan Sala y Usuario
│   │       └── equipamiento_service.py
│   ├── domain/
│   │   ├── entities.py              # Entidades: Sala, Usuario, Reserva, Equipamiento
│   │   └── reglas_negocio.py        # Reglas de negocio del dominio
│   ├── infrastructure/
│   │   └── repositories/            # Acceso a datos (una clase por entidad)
│   │       ├── sala_repository.py
│   │       ├── usuario_repository.py
│   │       ├── reserva_repository.py
│   │       └── equipamiento_repository.py
│   └── shared/
│       └── in_memory_store.py       # Almacenamiento en memoria (se reemplaza por la BD)
├── tests_manual/                    # Pruebas manuales de los endpoints (.http)
│   ├── pruebas_sala.http
│   ├── pruebas_usuario.http
│   ├── pruebas_reserva.http
│   └── pruebas_equipamiento.http
├── .env.example                     # Variables de entorno de ejemplo
├── requirements.txt                 # Dependencias del proyecto
└── README.md
```

**Nota:** los datos se guardan en una base SQLite (`reservas.db`) y se conservan al reiniciar el servidor.

## Ejecución de pruebas

Para reproducir la batería de pruebas y verificar el comportamiento de la API:

1. **Pruebas mediante archivos `.http` (REST Client):**
   - En VS Code, instala la extensión **REST Client**.
   - Abre la carpeta `tests_manual/` y ejecuta los archivos de solicitudes:
     - `pruebas_usuario.http`: Creación (201), duplicados (409) y no encontrado (404).
     - `pruebas_sala.http`: CRUD de salas y consultas con filtro/paginación (200).
     - `pruebas_equipamiento.http`: Cambio de estado de equipamiento (200).
     - `pruebas_reserva.http`: Creación, confirmación (200) y solapamiento de horario (409).

2. **Informe de evidencias de Calidad y Pruebas:**
   - La matriz detallada con los casos de prueba, resultados esperados vs. obtenidos y capturas de pantalla de evidencias se encuentra documentada en `tests_manual/informe_pruebas.md`.
   - Las imágenes asociadas a las evidencias se almacenan en la carpeta `tests_manual/capturas/`.

3. **Verificación de Persistencia tras Reinicio:**
   - Se incluye el script `tests_manual/verificar_persistencia.py` para comprobar que las modificaciones permanecen guardadas en la base de datos `reservas.db` tras reiniciar el proceso de Uvicorn.