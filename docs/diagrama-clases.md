# Diagrama de clases

Arquitectura por capas: **presentación → aplicación → dominio ← infraestructura**.
El dominio no importa FastAPI ni SQLAlchemy; la infraestructura implementa la
persistencia y los mappers traducen entre entidades y modelos ORM.

```mermaid
classDiagram
    direction LR

    %% ---------- DOMINIO ----------
    namespace Dominio {
        class Usuario {
            +int id
            +str nombre
            +str correo
            +RolUsuario rol
            +bool activo
            +str password_hash
            +int intentos_fallidos
            +datetime bloqueado_hasta
        }
        class Sala {
            +int id
            +str nombre
            +int capacidad
            +str ubicacion
            +EstadoSala estado
        }
        class Equipamiento {
            +int id
            +str nombre
            +str tipo
            +EstadoEquipamiento estado
            +int sala_id
            +str descripcion
        }
        class Reserva {
            +int id
            +int usuario_id
            +int sala_id
            +datetime fecha_inicio
            +datetime fecha_fin
            +str proposito
            +int num_asistentes
            +EstadoReserva estado
        }
        class ReglasNegocio {
            <<module>>
            +validar_fechas_reserva()
            +validar_disponibilidad_sala()
            +validar_equipamiento_disponible()
            +validar_capacidad_sala()
            +validar_sala_operativa()
        }
    }

    %% ---------- APLICACIÓN ----------
    namespace Aplicacion {
        class AuthService {
            +registrar()
            +login()
            +refrescar()
            +logout()
            +solicitar_recuperacion()
            +restablecer_password()
            +usuario_desde_token()
        }
        class ReservaService {
            +crear_reserva()
            +confirmar_reserva()
            +cancelar_reserva()
            +listar_reservas_paginado()
        }
        class SalaService {
            +listar_salas()
            +consultar_disponibilidad()
            +obtener_sala_con_equipamiento()
        }
        class UsuarioService
        class EquipamientoService
    }

    %% ---------- INFRAESTRUCTURA ----------
    namespace Infraestructura {
        class UsuarioRepository
        class SalaRepository
        class ReservaRepository
        class EquipamientoRepository
        class RefreshTokenRepository
        class RecuperacionTokenRepository
        class UsuarioModel {
            <<ORM>>
        }
        class SalaModel {
            <<ORM>>
        }
        class ReservaModel {
            <<ORM>>
        }
        class EquipamientoModel {
            <<ORM>>
        }
    }

    %% ---------- PRESENTACIÓN ----------
    namespace Presentacion {
        class Routers {
            <<FastAPI>>
            +auth_router
            +sala_router
            +usuario_router
            +equipamiento_router
            +reserva_router
        }
        class DTOs {
            <<Pydantic>>
        }
        class Dependencias {
            <<FastAPI>>
            +get_db()
            +get_current_user()
            +require_admin()
        }
    }

    Routers --> Dependencias
    Routers --> AuthService
    Routers --> ReservaService
    Routers --> SalaService
    Routers --> UsuarioService
    Routers --> EquipamientoService
    Routers --> DTOs

    AuthService --> UsuarioRepository
    AuthService --> RefreshTokenRepository
    AuthService --> RecuperacionTokenRepository
    ReservaService --> ReservaRepository
    ReservaService --> SalaRepository
    ReservaService --> ReglasNegocio
    SalaService --> SalaRepository
    SalaService --> EquipamientoRepository

    UsuarioRepository --> UsuarioModel
    SalaRepository --> SalaModel
    ReservaRepository --> ReservaModel
    EquipamientoRepository --> EquipamientoModel

    UsuarioModel ..> Usuario : mapper
    SalaModel ..> Sala : mapper
    ReservaModel ..> Reserva : mapper
    EquipamientoModel ..> Equipamiento : mapper
```

## Flujo de una petición

```
Cliente HTTP
   │  JSON + Bearer token
   ▼
Router (presentación)  ── valida DTO, aplica dependencias (401/403)
   │
   ▼
Service (aplicación)   ── casos de uso y transacciones
   │
   ▼
Reglas de negocio (dominio)  ── reglas puras, sin framework
   │
   ▼
Repository (infraestructura) ── consultas SQLAlchemy
   │
   ▼
Modelo ORM ──► Base de datos (SQLite / PostgreSQL)
```

## Dependencias entre capas

| Capa | Puede importar | No puede importar |
|---|---|---|
| Dominio | Solo biblioteca estándar | FastAPI, SQLAlchemy, Pydantic |
| Aplicación | Dominio, repositorios, DTOs | Routers |
| Infraestructura | Dominio, SQLAlchemy | Routers |
| Presentación | Aplicación, dominio, DTOs | SQLAlchemy directo (usa repositorios) |
