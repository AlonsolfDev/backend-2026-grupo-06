"""
Repositorio de Equipamiento: instancia del almacén en memoria específico para esta entidad.
"""
from app.shared.in_memory_store import InMemoryStore
from app.domain.entities import Equipamiento

equipamiento_store: InMemoryStore[Equipamiento] = InMemoryStore()