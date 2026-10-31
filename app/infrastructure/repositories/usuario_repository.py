"""
Repositorio de Usuario: instancia del almacén en memoria específico para esta entidad.
"""
from app.shared.in_memory_store import InMemoryStore
from app.domain.entities import Usuario

usuario_store: InMemoryStore[Usuario] = InMemoryStore()