"""
reservations/model.py — Documento Beanie que representa la colección 'reservations'.

Relaciones (referencing, estilo MongoDB):
  - guest_id → ObjectId que apunta a la colección 'guests'
  - room_id  → ObjectId que apunta a la colección 'rooms'

Las fechas y el estado se almacenan EMBEBIDOS directamente en este documento,
lo que permite consultas de disponibilidad sin JOINs costosos.

Diagrama:
  Guest (1) ←── guest_id ──── Reservation (N) ──── room_id ──► Room (1)
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import ASCENDING, IndexModel


class ReservationStatus(str, Enum):
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    COMPLETADA = "Completada"


class Reservation(Document):
    """
    Representa una reserva en el sistema.

    Campos referenciados (FK por ObjectId):
      - guest_id → huésped que realiza la reserva
      - room_id  → habitación asignada

    Campos embebidos (evitan lookups en consultas de disponibilidad):
      - check_in / check_out → rango de fechas de la estancia
      - status               → estado actual de la reserva
      - total_price          → precio calculado al momento de crear la reserva
    """

    guest_id: PydanticObjectId
    room_id: PydanticObjectId

    check_in: date
    check_out: date

    status: ReservationStatus = ReservationStatus.CONFIRMADA
    total_price: float = Field(..., ge=0)

    notes: Optional[str] = Field(None, max_length=500)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "reservations"
        indexes = [
            # Consultas de disponibilidad de habitación
            IndexModel([("room_id", ASCENDING), ("check_in", ASCENDING), ("check_out", ASCENDING)]),
            # Historial por huésped
            IndexModel([("guest_id", ASCENDING)]),
            # Filtrado por estado
            IndexModel([("status", ASCENDING)]),
        ]
