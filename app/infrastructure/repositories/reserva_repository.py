"""
Repositorio de Reserva: instancia del almacén en memoria específico para esta entidad.
"""
from app.shared.in_memory_store import InMemoryStore
from app.domain.entities import Reserva

reserva_store: InMemoryStore[Reserva] = InMemoryStore()