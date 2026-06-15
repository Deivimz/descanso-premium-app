"""
rooms/repository.py — Repositorio de habitaciones.
Extiende BaseRepository con consultas específicas del dominio.
"""

from __future__ import annotations

from typing import Optional

from app.rooms.model import Room, RoomState
from app.shared.base_repository import BaseRepository


class RoomRepository(BaseRepository[Room]):
    def __init__(self):
        super().__init__(Room)

    async def find_by_number(self, number: str) -> Optional[Room]:
        """Busca una habitación por su número único."""
        return await Room.find_one(Room.number == number)

    async def find_available(self) -> list[Room]:
        """Retorna todas las habitaciones en estado DISPONIBLE y activas."""
        return await Room.find(
            Room.state == RoomState.DISPONIBLE,
            Room.is_active == True,
        ).to_list()

    async def find_active(self, skip: int = 0, limit: int = 100) -> list[Room]:
        """Retorna habitaciones activas paginadas."""
        return (
            await Room.find(Room.is_active == True)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def count_active(self) -> int:
        return await Room.find(Room.is_active == True).count()
