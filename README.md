# Proyecto Backend - Grupo 6 (ICINF1108)

API REST para gestión de reservas de salas.

## Integrantes y responsabilidades

Jefe de grupo: Alonso Lantaño.

| Integrante | Responsabilidad principal |
|---|---|
| Alonso Lantaño | (por asignar) |
| Jesús Huentemil | (por asignar) |
| Tomás Mardones | (por asignar) |
| Diego Vásquez | (por asignar) |

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

(Pendiente: se completa cuando esté lista la persistencia con SQLAlchemy y Alembic.)

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

(Pendiente: diagrama router → servicio → repositorio → base de datos.)

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

**Nota:** en esta versión los datos se guardan en memoria; cada vez que se reinicia el servidor estos se pierden. Se reemplazará por una base de datos real con migraciones y seeders.

## Ejecución de pruebas

Los casos están en `tests_manual/` (archivos `.http`). (Pendiente: procedimiento de ejecución y evidencias con resultado esperado y obtenido.)