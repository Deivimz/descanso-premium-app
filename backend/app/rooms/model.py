"""
rooms/model.py — Documento Beanie que representa la colección 'rooms' en MongoDB.

Estados de habitación:
  - DISPONIBLE   → La habitación puede ser reservada.
  - OCUPADA      → Hay un huésped activo, no puede reservarse.
  - MANTENIMIENTO → Fuera de servicio, no puede reservarse.

Relaciones:
  - Room (1) ←── room_id ──── Reservation (N)
    La FK vive en el lado 'muchos' (Reservation), no aquí.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel


class RoomType(str, Enum):
    SIMPLE = "Simple"
    DOBLE = "Doble"
    SUITE = "Suite"
    PRESIDENCIAL = "Presidencial"


class RoomState(str, Enum):
    DISPONIBLE = "Disponible"
    OCUPADA = "Ocupada"
    MANTENIMIENTO = "Mantenimiento"


class Room(Document):
    """
    Representa una habitación del hotel.

    Campos:
      - number       → identificador único de la habitación (ej. '101', '202A')
      - room_type    → categoría (Simple, Doble, Suite, Presidencial)
      - capacity     → máximo de huéspedes permitidos
      - state        → estado actual (embebido directamente)
      - price_per_night → tarifa por noche en la moneda base
      - floor        → piso donde está la habitación (opcional)
      - description  → descripción breve de los amenities (opcional)
    """

    number: str = Field(..., min_length=1, max_length=10)
    room_type: RoomType = RoomType.SIMPLE
    capacity: int = Field(default=1, ge=1, le=20)
    state: RoomState = RoomState.DISPONIBLE
    price_per_night: float = Field(..., gt=0)
    floor: Optional[int] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=300)

    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "rooms"
        indexes = [
            IndexModel([("number", ASCENDING)], unique=True),
            IndexModel([("state", ASCENDING)]),
            IndexModel([("room_type", ASCENDING)]),
        ]
