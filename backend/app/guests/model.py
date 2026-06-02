"""
guests/model.py — Documento Beanie que representa la colección 'guests' en MongoDB.

Diseño para relaciones futuras:
  - Guest NO almacena referencias a Booking ni a Room.
  - Booking (Paso 3) tendrá: guest_id: PydanticObjectId
  - Esta separación evita el acoplamiento bidireccional y sigue el estándar
    de referencing de MongoDB: la FK vive en el lado "muchos" (Booking).

  Diagrama futuro:
    Guest (1) ←── guest_id ──── Booking (N)
                                   └── room_id ──► Room (1)
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from beanie import Document
from pydantic import EmailStr, Field
from pymongo import ASCENDING, IndexModel


# ---------------------------------------------------------------------------
# Enumerados del dominio — se importan también desde schemas.py
# ---------------------------------------------------------------------------

class DocumentType(str, Enum):
    DNI = "DNI"
    PASAPORTE = "PASAPORTE"
    RUC = "RUC"
    CE = "CE"


# ---------------------------------------------------------------------------
# Documento Beanie
# ---------------------------------------------------------------------------

class Guest(Document):
    """
    Representa un huésped registrado en el sistema.

    Campos de identidad:
      - email        → único, índice
      - document_number → único, índice (combinado con document_type)

    Campos de auditoría:
      - is_active    → soft-delete: False no borra el registro
      - created_at / updated_at → timestamps automáticos
    """

    # ── Datos personales ──────────────────────────────────────────────────
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=60)
    address: Optional[str] = Field(None, max_length=200)

    # ── Documento de identidad ────────────────────────────────────────────
    document_type: DocumentType
    document_number: str = Field(..., min_length=5, max_length=20)

    # ── Notas internas ────────────────────────────────────────────────────
    notes: Optional[str] = Field(None, max_length=500)

    # ── Auditoría ─────────────────────────────────────────────────────────
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # ── Configuración Beanie ──────────────────────────────────────────────
    class Settings:
        name = "guests"           # nombre de la colección en MongoDB
        indexes = [
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("document_number", ASCENDING)], unique=True),
            IndexModel([("is_active", ASCENDING)]),
            # Índice compuesto para búsqueda por nombre (listados, autocompletado)
            IndexModel(
                [("last_name", ASCENDING), ("first_name", ASCENDING)],
                name="idx_full_name",
            ),
        ]
