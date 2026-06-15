"""
reservations/schemas.py — Schemas Pydantic para el módulo de Reservas.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.reservations.model import ReservationStatus


# ---------------------------------------------------------------------------
# Input schemas
# ---------------------------------------------------------------------------

class ReservationCreate(BaseModel):
    guest_id: str = Field(..., description="ObjectId del huésped")
    room_id: str = Field(..., description="ObjectId de la habitación")
    check_in: date
    check_out: date
    notes: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.check_out <= self.check_in:
            raise ValueError("La fecha de check-out debe ser posterior al check-in.")
        return self


class ReservationUpdate(BaseModel):
    """Solo se permite actualizar notas o cancelar una reserva."""
    status: Optional[ReservationStatus] = None
    notes: Optional[str] = Field(None, max_length=500)


# ---------------------------------------------------------------------------
# Output schemas
# ---------------------------------------------------------------------------

class ReservationResponse(BaseModel):
    id: str
    guest_id: str
    room_id: str
    check_in: date
    check_out: date
    status: ReservationStatus
    total_price: float
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_document(cls, r) -> "ReservationResponse":
        return cls(
            id=str(r.id),
            guest_id=str(r.guest_id),
            room_id=str(r.room_id),
            check_in=r.check_in,
            check_out=r.check_out,
            status=r.status,
            total_price=r.total_price,
            notes=r.notes,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )


class ReservationListResponse(BaseModel):
    items: list[ReservationResponse]
    total: int
    skip: int
    limit: int
