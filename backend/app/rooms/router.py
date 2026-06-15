"""
rooms/router.py — Endpoints REST del módulo de Habitaciones.
Prefijo: /api/rooms
Todos los endpoints requieren autenticación JWT.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_user
from app.rooms.model import RoomState
from app.rooms.schemas import (
    RoomCreate,
    RoomListResponse,
    RoomResponse,
    RoomStateUpdate,
    RoomUpdate,
)
from app.rooms.service import RoomService
from app.users.model import User

router = APIRouter(prefix="/api/rooms", tags=["Rooms"])


def get_service() -> RoomService:
    return RoomService()


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    data: RoomCreate,
    service: RoomService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """Crea una nueva habitación. Solo administradores."""
    room = await service.create_room(data)
    return RoomResponse.from_document(room)


@router.get("", response_model=RoomListResponse)
async def list_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    only_available: bool = Query(False, description="Si es true, solo devuelve las habitaciones disponibles."),
    service: RoomService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """Lista todas las habitaciones con paginación opcional."""
    rooms, total = await service.list_rooms(skip, limit, only_available)
    return RoomListResponse(
        items=[RoomResponse.from_document(r) for r in rooms],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: str,
    service: RoomService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """Obtiene una habitación por su ID."""
    room = await service.get_room_or_404(room_id)
    return RoomResponse.from_document(room)


@router.patch("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: str,
    data: RoomUpdate,
    service: RoomService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """Actualiza parcialmente los datos de una habitación."""
    room = await service.update_room(room_id, data)
    return RoomResponse.from_document(room)


@router.patch("/{room_id}/state", response_model=RoomResponse)
async def change_room_state(
    room_id: str,
    data: RoomStateUpdate,
    service: RoomService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """Cambia el estado de una habitación (Disponible / Ocupada / Mantenimiento)."""
    room = await service.change_state(room_id, data.state)
    return RoomResponse.from_document(room)


@router.delete("/{room_id}", response_model=RoomResponse)
async def deactivate_room(
    room_id: str,
    service: RoomService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    """Desactiva (soft-delete) una habitación. No permitido si está Ocupada."""
    room = await service.deactivate_room(room_id)
    return RoomResponse.from_document(room)
