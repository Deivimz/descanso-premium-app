"""
guests/schemas.py — DTOs Pydantic para el módulo de Huéspedes.

Convención:
  GuestCreate       → payload del cliente en POST /api/guests
  GuestUpdate       → payload del cliente en PATCH /api/guests/{id}
  GuestResponse     → lo que devuelve la API en cada operación
  GuestListResponse → respuesta paginada del listado
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.shared.validators import is_valid_rut

# Importamos el enum desde el modelo (fuente de verdad del dominio)
from app.guests.model import DocumentType


# ---------------------------------------------------------------------------
# CREATE — POST /api/guests
# ---------------------------------------------------------------------------

class GuestCreate(BaseModel):
    """Campos requeridos para registrar un nuevo huésped."""

    first_name: str = Field(..., min_length=2, max_length=100, examples=["María"])
    last_name: str = Field(..., min_length=2, max_length=100, examples=["González"])
    email: EmailStr = Field(..., examples=["maria.gonzalez@email.com"])
    phone: Optional[str] = Field(None, max_length=20, examples=["+58 412 555 0101"])
    date_of_birth: Optional[date] = Field(None, examples=["1990-05-15"])
    nationality: Optional[str] = Field(None, max_length=60, examples=["Venezolana"])
    address: Optional[str] = Field(None, max_length=200, examples=["Av. Principal, Caracas"])
    document_type: DocumentType = Field(..., examples=[DocumentType.RUT])
    document_number: str = Field(..., min_length=5, max_length=20, examples=["V-12345678"])
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("document_number")
    @classmethod
    def normalize_document_number(cls, v: str, info) -> str:
        doc_type = info.data.get("document_type")
        v = v.strip().upper()
        if doc_type == DocumentType.RUT and not is_valid_rut(v):
            raise ValueError("RUT no es válido")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def capitalize_name(cls, v: str) -> str:
        return v.strip().title()


# ---------------------------------------------------------------------------
# UPDATE — PATCH /api/guests/{id}
# ---------------------------------------------------------------------------

class GuestUpdate(BaseModel):
    """Campos opcionales para actualización parcial de un huésped."""

    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=60)
    address: Optional[str] = Field(None, max_length=200)
    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = Field(None, min_length=5, max_length=20)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("document_number")
    @classmethod
    def normalize_document_number(cls, v: Optional[str], info) -> Optional[str]:
        if not v:
            return v
        doc_type = info.data.get("document_type")
        v = v.strip().upper()
        # En PATCH, si mandan RUT pero no document_type, no validamos Módulo 11
        # a menos que sepamos que es RUT (se tendría que cruzar con BD, pero info.data solo tiene payload actual).
        # Hacemos validación condicional.
        if doc_type == DocumentType.RUT and not is_valid_rut(v):
            raise ValueError("RUT no es válido")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def capitalize_name(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().title() if v else v


# ---------------------------------------------------------------------------
# RESPONSE — lo que devuelve la API
# ---------------------------------------------------------------------------

class GuestResponse(BaseModel):
    """Representación completa de un huésped en las respuestas de la API."""

    id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    document_type: DocumentType
    document_number: str
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# LIST RESPONSE — respuesta paginada
# ---------------------------------------------------------------------------

class GuestListResponse(BaseModel):
    """Respuesta paginada del listado de huéspedes."""

    items: list[GuestResponse]
    total: int = Field(..., description="Total de registros que coinciden con el filtro")
    page: int = Field(..., description="Página actual (base 1)")
    size: int = Field(..., description="Registros por página")
    pages: int = Field(..., description="Total de páginas")
