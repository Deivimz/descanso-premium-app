"""
reservations/service.py — Lógica de negocio del módulo de Reservas.

Implementa las 3 reglas de negocio clave del proyecto:
  1. Sin reservas para fechas pasadas.
  2. Sin double-booking de habitación.
  3. Un huésped no puede tener dos reservas activas en las mismas fechas.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from beanie import PydanticObjectId
from fastapi import HTTPException, status

from app.guests.model import Guest
from app.reservations.model import Reservation, ReservationStatus
from app.reservations.repository import ReservationRepository
from app.reservations.schemas import ReservationCreate, ReservationUpdate
from app.rooms.model import Room, RoomState
from app.rooms.repository import RoomRepository


class ReservationService:
    def __init__(self):
        self.repo = ReservationRepository()
        self.room_repo = RoomRepository()

    # ------------------------------------------------------------------
    # Helpers de validación
    # ------------------------------------------------------------------

    def _validate_dates(self, check_in: date, check_out: date) -> None:
        """Regla 1: No se permiten reservas con fechas pasadas."""
        today = datetime.now(timezone.utc).date()
        if check_in < today:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La fecha de check-in no puede ser una fecha pasada.",
            )
        if check_out <= check_in:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La fecha de check-out debe ser posterior al check-in.",
            )

    async def _validate_room_availability(
        self,
        room_id: PydanticObjectId,
        check_in: date,
        check_out: date,
        exclude_id: PydanticObjectId | None = None,
    ) -> None:
        """Regla 2: No double-booking de habitación."""
        conflicts = await self.repo.find_overlapping_for_room(
            room_id, check_in, check_out, exclude_id
        )
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "La habitación ya tiene una reserva confirmada en ese rango de fechas. "
                    "Seleccione otras fechas u otra habitación."
                ),
            )

    async def _validate_guest_availability(
        self,
        guest_id: PydanticObjectId,
        check_in: date,
        check_out: date,
        exclude_id: PydanticObjectId | None = None,
    ) -> None:
        """Regla 3: Un huésped no puede tener dos reservas activas en las mismas fechas."""
        conflicts = await self.repo.find_overlapping_for_guest(
            guest_id, check_in, check_out, exclude_id
        )
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "El huésped ya tiene una reserva activa en ese rango de fechas. "
                    "Un huésped no puede tener más de una reserva simultánea."
                ),
            )

    # ------------------------------------------------------------------
    # Operaciones
    # ------------------------------------------------------------------

    async def create_reservation(self, data: ReservationCreate) -> Reservation:
        # Parsear IDs
        try:
            guest_oid = PydanticObjectId(data.guest_id)
            room_oid = PydanticObjectId(data.room_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El guest_id o room_id proporcionado no es un ObjectId válido.",
            )

        # Verificar que el huésped existe y está activo
        guest = await Guest.get(guest_oid)
        if not guest or not guest.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Huésped '{data.guest_id}' no encontrado o inactivo.",
            )

        # Verificar que la habitación existe y está activa
        room = await Room.get(room_oid)
        if not room or not room.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Habitación '{data.room_id}' no encontrada o inactiva.",
            )

        # Verificar que la habitación no está en mantenimiento
        if room.state == RoomState.MANTENIMIENTO:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La habitación está en mantenimiento y no puede ser reservada.",
            )

        # Regla 1: fechas futuras
        self._validate_dates(data.check_in, data.check_out)

        # Regla 2: disponibilidad de habitación
        await self._validate_room_availability(room_oid, data.check_in, data.check_out)

        # Regla 3: disponibilidad de huésped
        await self._validate_guest_availability(guest_oid, data.check_in, data.check_out)

        # Calcular precio total
        nights = (data.check_out - data.check_in).days
        total_price = nights * room.price_per_night

        reservation = Reservation(
            guest_id=guest_oid,
            room_id=room_oid,
            check_in=data.check_in,
            check_out=data.check_out,
            total_price=total_price,
            notes=data.notes,
            status=ReservationStatus.CONFIRMADA,
        )
        return await self.repo.create(reservation)

    async def get_reservation_or_404(self, reservation_id: str) -> Reservation:
        r = await self.repo.find_by_id(reservation_id)
        if not r:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reserva '{reservation_id}' no encontrada.",
            )
        return r

    async def list_reservations(self, skip: int, limit: int) -> tuple[list[Reservation], int]:
        items = await Reservation.find_all().skip(skip).limit(limit).to_list()
        total = await self.repo.count_all()
        return items, total

    async def get_guest_history(
        self, guest_id: str, skip: int, limit: int
    ) -> tuple[list[Reservation], int]:
        try:
            guest_oid = PydanticObjectId(guest_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="guest_id no válido.",
            )
        items = await self.repo.find_by_guest(guest_oid, skip, limit)
        total = await self.repo.count_by_guest(guest_oid)
        return items, total

    async def update_reservation(self, reservation_id: str, data: ReservationUpdate) -> Reservation:
        r = await self.get_reservation_or_404(reservation_id)

        if r.status == ReservationStatus.COMPLETADA:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede modificar una reserva completada.",
            )

        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se enviaron campos para actualizar.",
            )
        return await self.repo.update(r, update_data)

    async def cancel_reservation(self, reservation_id: str) -> Reservation:
        r = await self.get_reservation_or_404(reservation_id)
        if r.status == ReservationStatus.CANCELADA:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La reserva ya está cancelada.",
            )
        return await self.repo.update(r, {"status": ReservationStatus.CANCELADA})

    async def complete_reservation(self, reservation_id: str) -> Reservation:
        r = await self.get_reservation_or_404(reservation_id)
        if r.status != ReservationStatus.CONFIRMADA:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden completar reservas con estado 'Confirmada'.",
            )
        return await self.repo.update(r, {"status": ReservationStatus.COMPLETADA})
