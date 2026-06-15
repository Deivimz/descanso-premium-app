"""
rooms/service.py — Lógica de negocio del módulo de Habitaciones.
"""

from __future__ import annotations

from fastapi import HTTPException, status

from app.rooms.model import Room, RoomState
from app.rooms.repository import RoomRepository
from app.rooms.schemas import RoomCreate, RoomUpdate


class RoomService:
    def __init__(self):
        self.repo = RoomRepository()

    async def create_room(self, data: RoomCreate) -> Room:
        # Número único
        existing = await self.repo.find_by_number(data.number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe una habitación con el número '{data.number}'.",
            )

        room = Room(
            number=data.number,
            room_type=data.room_type,
            capacity=data.capacity,
            price_per_night=data.price_per_night,
            floor=data.floor,
            description=data.description,
            state=RoomState.DISPONIBLE,
        )
        return await self.repo.create(room)

    async def get_room_or_404(self, room_id: str) -> Room:
        room = await self.repo.find_by_id(room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Habitación '{room_id}' no encontrada.",
            )
        return room

    async def list_rooms(self, skip: int, limit: int, only_available: bool) -> tuple[list[Room], int]:
        if only_available:
            rooms = await self.repo.find_available()
            return rooms, len(rooms)
        rooms = await self.repo.find_active(skip, limit)
        total = await self.repo.count_active()
        return rooms, total

    async def update_room(self, room_id: str, data: RoomUpdate) -> Room:
        room = await self.get_room_or_404(room_id)
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se enviaron campos para actualizar.",
            )
        return await self.repo.update(room, update_data)

    async def change_state(self, room_id: str, new_state: RoomState) -> Room:
        room = await self.get_room_or_404(room_id)
        return await self.repo.update(room, {"state": new_state})

    async def deactivate_room(self, room_id: str) -> Room:
        """Soft-delete: marca la habitación como inactiva."""
        room = await self.get_room_or_404(room_id)
        if room.state == RoomState.OCUPADA:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede desactivar una habitación que está ocupada.",
            )
        return await self.repo.soft_delete(room)
