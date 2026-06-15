"""
reservations/repository.py — Repositorio de reservas.
Contiene las consultas de disponibilidad que implementan las reglas de negocio.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from beanie import PydanticObjectId

from app.reservations.model import Reservation, ReservationStatus
from app.shared.base_repository import BaseRepository


class ReservationRepository(BaseRepository[Reservation]):
    def __init__(self):
        super().__init__(Reservation)

    async def find_overlapping_for_room(
        self,
        room_id: PydanticObjectId,
        check_in: date,
        check_out: date,
        exclude_reservation_id: Optional[PydanticObjectId] = None,
    ) -> list[Reservation]:
        """
        Busca reservas CONFIRMADAS para una habitación que se solapen con el rango dado.

        La condición de solapamiento es:
            existing.check_in < requested.check_out
            AND
            existing.check_out > requested.check_in

        Esto cubre todos los casos:
            ├── Reserva existente contiene la nueva
            ├── Nueva reserva contiene la existente
            ├── Solapamiento izquierdo
            └── Solapamiento derecho
        """
        query = {
            "room_id": room_id,
            "status": ReservationStatus.CONFIRMADA,
            "check_in": {"$lt": check_out},
            "check_out": {"$gt": check_in},
        }
        if exclude_reservation_id:
            query["_id"] = {"$ne": exclude_reservation_id}

        return await Reservation.find(query).to_list()

    async def find_overlapping_for_guest(
        self,
        guest_id: PydanticObjectId,
        check_in: date,
        check_out: date,
        exclude_reservation_id: Optional[PydanticObjectId] = None,
    ) -> list[Reservation]:
        """
        Busca reservas CONFIRMADAS de un huésped que se solapen con el rango dado.
        Garantiza que un mismo huésped no tenga dos reservas activas en fechas coincidentes.
        """
        query = {
            "guest_id": guest_id,
            "status": ReservationStatus.CONFIRMADA,
            "check_in": {"$lt": check_out},
            "check_out": {"$gt": check_in},
        }
        if exclude_reservation_id:
            query["_id"] = {"$ne": exclude_reservation_id}

        return await Reservation.find(query).to_list()

    async def find_by_guest(
        self, guest_id: PydanticObjectId, skip: int = 0, limit: int = 100
    ) -> list[Reservation]:
        """Historial completo (pasadas y futuras) de un huésped."""
        return (
            await Reservation.find(Reservation.guest_id == guest_id)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def count_by_guest(self, guest_id: PydanticObjectId) -> int:
        return await Reservation.find(Reservation.guest_id == guest_id).count()

    async def find_active(self, skip: int = 0, limit: int = 100) -> list[Reservation]:
        return (
            await Reservation.find(
                Reservation.status == ReservationStatus.CONFIRMADA
            )
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def count_all(self) -> int:
        return await Reservation.find_all().count()
