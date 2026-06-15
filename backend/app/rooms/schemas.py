"""
rooms/schemas.py — Schemas Pydantic para el módulo de Habitaciones.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.rooms.model import RoomState, RoomType


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class RoomCreate(BaseModel):
    number: str = Field(..., min_length=1, max_length=10, examples=["101"])
    room_type: RoomType = RoomType.SIMPLE
    capacity: int = Field(default=1, ge=1, le=20)
    price_per_night: float = Field(..., gt=0, examples=[75000.0])
    floor: Optional[int] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=300)


class RoomUpdate(BaseModel):
    """Todos los campos son opcionales — PATCH parcial."""
    room_type: Optional[RoomType] = None
    capacity: Optional[int] = Field(None, ge=1, le=20)
    state: Optional[RoomState] = None
    price_per_night: Optional[float] = Field(None, gt=0)
    floor: Optional[int] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=300)
    is_active: Optional[bool] = None


class RoomStateUpdate(BaseModel):
    """Schema dedicado a cambiar solo el estado de una habitación."""
    state: RoomState


# ---------------------------------------------------------------------------
# Output schemas
# ---------------------------------------------------------------------------

class RoomResponse(BaseModel):
    id: str
    number: str
    room_type: RoomType
    capacity: int
    state: RoomState
    price_per_night: float
    floor: Optional[int]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_document(cls, room) -> "RoomResponse":
        return cls(
            id=str(room.id),
            number=room.number,
            room_type=room.room_type,
            capacity=room.capacity,
            state=room.state,
            price_per_night=room.price_per_night,
            floor=room.floor,
            description=room.description,
            is_active=room.is_active,
            created_at=room.created_at,
            updated_at=room.updated_at,
        )


class RoomListResponse(BaseModel):
    items: list[RoomResponse]
    total: int
    skip: int
    limit: int
