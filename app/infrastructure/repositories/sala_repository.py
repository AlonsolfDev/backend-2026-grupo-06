"""
Repositorio de Sala: instancia del almacén en memoria específico para esta entidad.
"""
from app.shared.in_memory_store import InMemoryStore
from app.domain.entities import Sala

sala_store: InMemoryStore[Sala] = InMemoryStore()