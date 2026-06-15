"""
reservations/router.py — Endpoints REST del módulo de Reservas.
Prefijo: /api/reservations
Todos los endpoints requieren autenticación JWT.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_user
from app.reservations.schemas import (
    ReservationCreate,
    ReservationListResponse,
    ReservationResponse,
    ReservationUpdate,
)
from app.reservations.service import ReservationService
from app.users.model import User

router = APIRouter(prefix="/api/reservations", tags=["Reservations"])


def get_service() -> ReservationService:
    return ReservationService()


@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    data: ReservationCreate,
    service: ReservationService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """
    Crea una reserva aplicando las 3 reglas de negocio:
    - No fechas pasadas.
    - No double-booking de habitación.
    - El huésped no puede tener dos reservas activas en las mismas fechas.
    """
    r = await service.create_reservation(data)
    return ReservationResponse.from_document(r)


@router.get("", response_model=ReservationListResponse)
async def list_reservations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: ReservationService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """Lista todas las reservas del sistema."""
    items, total = await service.list_reservations(skip, limit)
    return ReservationListResponse(
        items=[ReservationResponse.from_document(r) for r in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/guest/{guest_id}", response_model=ReservationListResponse)
async def get_guest_history(
    guest_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: ReservationService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """Historial completo de reservas (pasadas y futuras) de un huésped específico."""
    items, total = await service.get_guest_history(guest_id, skip, limit)
    return ReservationListResponse(
        items=[ReservationResponse.from_document(r) for r in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: str,
    service: ReservationService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """Obtiene una reserva por su ID."""
    r = await service.get_reservation_or_404(reservation_id)
    return ReservationResponse.from_document(r)


@router.patch("/{reservation_id}", response_model=ReservationResponse)
async def update_reservation(
    reservation_id: str,
    data: ReservationUpdate,
    service: ReservationService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """Actualiza el estado o las notas de una reserva."""
    r = await service.update_reservation(reservation_id, data)
    return ReservationResponse.from_document(r)


@router.patch("/{reservation_id}/cancel", response_model=ReservationResponse)
async def cancel_reservation(
    reservation_id: str,
    service: ReservationService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """Cancela una reserva confirmada."""
    r = await service.cancel_reservation(reservation_id)
    return ReservationResponse.from_document(r)


@router.patch("/{reservation_id}/complete", response_model=ReservationResponse)
async def complete_reservation(
    reservation_id: str,
    service: ReservationService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """Marca una reserva como completada (check-out realizado)."""
    r = await service.complete_reservation(reservation_id)
    return ReservationResponse.from_document(r)
