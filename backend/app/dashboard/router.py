"""
Endpoint GET /api/dashboard/stats — Estadísticas para el panel principal.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.guests.model import Guest
from app.rooms.model import Room, RoomState, RoomType
from app.reservations.model import Reservation, ReservationStatus
from app.users.model import User

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
):
    """
    Retorna un resumen consolidado para el dashboard:
      - Totales de huéspedes, habitaciones y reservas
      - Huéspedes actualmente en el hotel (check-in pasado, check-out futuro, CONFIRMADA)
      - Monto total de reservas confirmadas
      - Desglose de habitaciones por tipo y estado
      - Reservas por estado
    """
    today = datetime.now(timezone.utc).date()

    # ── Totales generales ───────────────────────────────────────────────────
    total_guests = await Guest.find(Guest.is_active == True).count()
    total_rooms = await Room.find(Room.is_active == True).count()
    total_reservations = await Reservation.find_all().count()

    # ── Huéspedes actualmente en el hotel ──────────────────────────────────
    # Reservas confirmadas cuyo check-in <= hoy y check-out > hoy
    guests_in_hotel_query = {
        "status": ReservationStatus.CONFIRMADA,
        "check_in": {"$lte": today},
        "check_out": {"$gt": today},
    }
    reservations_active_now = await Reservation.find(guests_in_hotel_query).to_list()
    guests_in_hotel = len(reservations_active_now)

    # ── Reservas por estado ────────────────────────────────────────────────
    confirmed_reservations = await Reservation.find(
        Reservation.status == ReservationStatus.CONFIRMADA
    ).to_list()
    cancelled_count = await Reservation.find(
        Reservation.status == ReservationStatus.CANCELADA
    ).count()
    completed_count = await Reservation.find(
        Reservation.status == ReservationStatus.COMPLETADA
    ).count()

    confirmed_count = len(confirmed_reservations)

    # Monto total de reservas CONFIRMADAS
    total_revenue_confirmed = sum(r.total_price for r in confirmed_reservations)

    # Monto total histórico (confirmadas + completadas)
    all_paid = await Reservation.find(
        {"status": {"$in": [ReservationStatus.CONFIRMADA, ReservationStatus.COMPLETADA]}}
    ).to_list()
    total_revenue_all = sum(r.total_price for r in all_paid)

    # ── Habitaciones por estado ────────────────────────────────────────────
    disponibles = await Room.find(
        Room.state == RoomState.DISPONIBLE, Room.is_active == True
    ).count()
    ocupadas = await Room.find(
        Room.state == RoomState.OCUPADA, Room.is_active == True
    ).count()
    mantenimiento = await Room.find(
        Room.state == RoomState.MANTENIMIENTO, Room.is_active == True
    ).count()

    # ── Habitaciones por tipo ──────────────────────────────────────────────
    rooms_by_type = {}
    for room_type in RoomType:
        count = await Room.find(
            Room.room_type == room_type, Room.is_active == True
        ).count()
        occupied = await Room.find(
            Room.room_type == room_type,
            Room.state == RoomState.OCUPADA,
            Room.is_active == True,
        ).count()
        rooms_by_type[room_type.value] = {
            "total": count,
            "disponible": count - occupied - await Room.find(
                Room.room_type == room_type,
                Room.state == RoomState.MANTENIMIENTO,
                Room.is_active == True,
            ).count(),
            "ocupada": occupied,
            "mantenimiento": await Room.find(
                Room.room_type == room_type,
                Room.state == RoomState.MANTENIMIENTO,
                Room.is_active == True,
            ).count(),
        }

    return {
        "guests": {
            "total_active": total_guests,
            "currently_in_hotel": guests_in_hotel,
        },
        "rooms": {
            "total": total_rooms,
            "disponible": disponibles,
            "ocupada": ocupadas,
            "mantenimiento": mantenimiento,
            "by_type": rooms_by_type,
        },
        "reservations": {
            "total": total_reservations,
            "confirmada": confirmed_count,
            "cancelada": cancelled_count,
            "completada": completed_count,
        },
        "revenue": {
            "confirmed_total_clp": total_revenue_confirmed,
            "historical_total_clp": total_revenue_all,
        },
    }
