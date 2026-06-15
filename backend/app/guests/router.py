"""
guests/router.py — Endpoints FastAPI del módulo de Huéspedes.

Prefijo: /api/guests
Tag:     Guests

Rutas expuestas:
  POST   /api/guests              → Crear huésped
  GET    /api/guests              → Listar (paginado + búsqueda)
  GET    /api/guests/{id}         → Obtener por id
  PATCH  /api/guests/{id}         → Actualización parcial
  DELETE /api/guests/{id}         → Soft-delete
  GET    /api/guests/{id}/bookings → Reservas del huésped (preparado para Paso 3)
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.guests.schemas import (
    GuestCreate,
    GuestListResponse,
    GuestResponse,
    GuestUpdate,
)
from app.guests.service import GuestService

router = APIRouter(
    prefix="/api/guests",
    tags=["Guests"],
    redirect_slashes=False,   # evita 307 que rompe POST/PATCH/DELETE en algunos clientes
)


# ---------------------------------------------------------------------------
# Dependencia — inyecta el servicio en cada endpoint
# ---------------------------------------------------------------------------

def get_service() -> GuestService:
    return GuestService()


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=GuestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo huésped",
    responses={
        409: {"description": "Email o número de documento ya registrado"},
        422: {"description": "Datos de entrada inválidos"},
    },
)
async def create_guest(
    data: GuestCreate,
    svc: GuestService = Depends(get_service),
) -> GuestResponse:
    """Crea un nuevo huésped verificando unicidad de email y documento."""
    return await svc.create_guest(data)


# ---------------------------------------------------------------------------
# LIST
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=GuestListResponse,
    summary="Listar huéspedes",
)
async def list_guests(
    page: int = Query(1, ge=1, description="Página actual (base 1)"),
    size: int = Query(20, ge=1, le=500, description="Registros por página"),
    search: Optional[str] = Query(None, description="Búsqueda libre en nombre, email, documento"),
    include_inactive: bool = Query(False, description="Incluir huéspedes inactivos"),
    svc: GuestService = Depends(get_service),
) -> GuestListResponse:
    """Lista huéspedes con paginación y filtro de búsqueda opcional."""
    return await svc.list_guests(
        page=page,
        size=size,
        search=search,
        include_inactive=include_inactive,
    )


# ---------------------------------------------------------------------------
# READ ONE
# ---------------------------------------------------------------------------

@router.get(
    "/{id}",
    response_model=GuestResponse,
    summary="Obtener un huésped por ID",
    responses={404: {"description": "Huésped no encontrado"}},
)
async def get_guest(
    id: str,
    svc: GuestService = Depends(get_service),
) -> GuestResponse:
    """Devuelve los datos completos de un huésped dado su id."""
    return await svc.get_guest(id)


# ---------------------------------------------------------------------------
# UPDATE (PATCH parcial)
# ---------------------------------------------------------------------------

@router.patch(
    "/{id}",
    response_model=GuestResponse,
    summary="Actualizar parcialmente un huésped",
    responses={
        404: {"description": "Huésped no encontrado"},
        409: {"description": "Email o documento ya en uso por otro huésped"},
    },
)
async def update_guest(
    id: str,
    data: GuestUpdate,
    svc: GuestService = Depends(get_service),
) -> GuestResponse:
    """Actualiza solo los campos enviados en el cuerpo (PATCH semántico)."""
    return await svc.update_guest(id, data)


# ---------------------------------------------------------------------------
# DELETE (soft)
# ---------------------------------------------------------------------------

@router.delete(
    "/{id}",
    summary="Desactivar un huésped (soft-delete)",
    responses={
        404: {"description": "Huésped no encontrado"},
        409: {"description": "El huésped ya está inactivo"},
    },
)
async def delete_guest(
    id: str,
    svc: GuestService = Depends(get_service),
) -> dict:
    """
    Desactiva el huésped (is_active = False).
    El registro se conserva para mantener el historial de reservas.
    """
    return await svc.delete_guest(id)


# ---------------------------------------------------------------------------
# BOOKINGS (preparado para Paso 3)
# ---------------------------------------------------------------------------

@router.get(
    "/{id}/bookings",
    summary="Reservas de un huésped",
    responses={404: {"description": "Huésped no encontrado"}},
)
async def get_guest_bookings(
    id: str,
    svc: GuestService = Depends(get_service),
) -> list:
    """
    Devuelve las reservas asociadas al huésped.
    Retorna lista vacía hasta que el módulo de Bookings esté implementado (Paso 3).
    """
    return await svc.get_guest_bookings(id)
