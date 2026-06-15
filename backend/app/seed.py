"""
seed.py — Script de datos de prueba para Descanso Premium.

Crea:
  - 20 Huéspedes
  - 50 Habitaciones (Simple, Doble, Suite, Presidencial)
  - Reservas variadas (Confirmada, Cancelada, Completada) con distintos rangos de fechas

Ejecución:
  Se llama automáticamente desde main.py en el lifespan si la BD está vacía,
  solo si la variable de entorno SEED_DATA=true está definida.
"""

import logging
from datetime import date, datetime, timedelta, timezone

from beanie import PydanticObjectId

from app.guests.model import Guest, DocumentType
from app.rooms.model import Room, RoomType, RoomState
from app.reservations.model import Reservation, ReservationStatus

logger = logging.getLogger(__name__)


GUESTS_DATA = [
    ("Ana", "González", "ana.gonzalez@email.com", "12.345.678-9", DocumentType.RUT, "Chilena"),
    ("Carlos", "Martínez", "carlos.martinez@email.com", "11.222.333-4", DocumentType.RUT, "Chilena"),
    ("Sofía", "Rodríguez", "sofia.rodriguez@email.com", "13.444.555-6", DocumentType.RUT, "Chilena"),
    ("Diego", "López", "diego.lopez@email.com", "14.666.777-8", DocumentType.RUT, "Chilena"),
    ("Valentina", "Pérez", "valentina.perez@email.com", "15.888.999-0", DocumentType.RUT, "Chilena"),
    ("Matías", "Soto", "matias.soto@email.com", "16.111.222-3", DocumentType.RUT, "Chilena"),
    ("Isabella", "Vargas", "isabella.vargas@email.com", "17.333.444-5", DocumentType.RUT, "Chilena"),
    ("Sebastián", "Castro", "sebastian.castro@email.com", "18.555.666-7", DocumentType.RUT, "Chilena"),
    ("Camila", "Morales", "camila.morales@email.com", "19.777.888-9", DocumentType.RUT, "Chilena"),
    ("Lucas", "Jiménez", "lucas.jimenez@email.com", "20.999.111-2", DocumentType.RUT, "Chilena"),
    ("Emily", "Johnson", "emily.johnson@email.com", "PA1234567", DocumentType.PASAPORTE, "Estadounidense"),
    ("James", "Smith", "james.smith@email.com", "PA2345678", DocumentType.PASAPORTE, "Inglés"),
    ("Marie", "Dupont", "marie.dupont@email.com", "PA3456789", DocumentType.PASAPORTE, "Francesa"),
    ("Hans", "Müller", "hans.muller@email.com", "PA4567890", DocumentType.PASAPORTE, "Alemán"),
    ("Yuki", "Tanaka", "yuki.tanaka@email.com", "PA5678901", DocumentType.PASAPORTE, "Japonesa"),
    ("Pedro", "Fernández", "pedro.fernandez@email.com", "21.100.200-3", DocumentType.RUT, "Chilena"),
    ("Renata", "Herrera", "renata.herrera@email.com", "22.300.400-5", DocumentType.RUT, "Chilena"),
    ("Gonzalo", "Ríos", "gonzalo.rios@email.com", "23.500.600-7", DocumentType.RUT, "Chilena"),
    ("Antonia", "Torres", "antonia.torres@email.com", "24.700.800-9", DocumentType.RUT, "Chilena"),
    ("Felipe", "Núñez", "felipe.nunez@email.com", "25.900.100-K", DocumentType.RUT, "Chilena"),
]

# (numero, tipo, capacidad, precio_noche, piso, descripcion)
ROOMS_DATA = [
    # Simple (15 habitaciones) — Piso 1 y 2
    ("101", RoomType.SIMPLE, 1, 45000, 1, "Habitación simple con vista al jardín"),
    ("102", RoomType.SIMPLE, 1, 45000, 1, "Habitación simple, cama matrimonial"),
    ("103", RoomType.SIMPLE, 2, 48000, 1, "Habitación simple con sofá cama"),
    ("104", RoomType.SIMPLE, 1, 45000, 1, "Habitación simple, piso 1"),
    ("105", RoomType.SIMPLE, 1, 45000, 1, "Habitación simple con baño privado"),
    ("201", RoomType.SIMPLE, 1, 47000, 2, "Habitación simple con vista al patio"),
    ("202", RoomType.SIMPLE, 2, 49000, 2, "Habitación simple amplia, piso 2"),
    ("203", RoomType.SIMPLE, 1, 46000, 2, "Habitación simple, piso 2"),
    ("204", RoomType.SIMPLE, 1, 46000, 2, "Habitación simple luminosa"),
    ("205", RoomType.SIMPLE, 1, 47000, 2, "Habitación simple con balcón"),
    ("206", RoomType.SIMPLE, 2, 49000, 2, "Habitación simple doble uso"),
    ("207", RoomType.SIMPLE, 1, 45000, 2, "Habitación simple económica"),
    ("208", RoomType.SIMPLE, 1, 46000, 2, "Habitación simple con escritorio"),
    ("209", RoomType.SIMPLE, 1, 47000, 2, "Habitación simple renovada"),
    ("210", RoomType.SIMPLE, 2, 50000, 2, "Habitación simple con vista al mar"),
    # Doble (15 habitaciones) — Piso 3 y 4
    ("301", RoomType.DOBLE, 2, 75000, 3, "Habitación doble con dos camas"),
    ("302", RoomType.DOBLE, 2, 75000, 3, "Habitación doble matrimonial"),
    ("303", RoomType.DOBLE, 3, 80000, 3, "Habitación doble con cama extra"),
    ("304", RoomType.DOBLE, 2, 77000, 3, "Habitación doble con bañera"),
    ("305", RoomType.DOBLE, 2, 78000, 3, "Habitación doble premium, piso 3"),
    ("306", RoomType.DOBLE, 4, 85000, 3, "Habitación doble familiar"),
    ("307", RoomType.DOBLE, 2, 76000, 3, "Habitación doble con vista al jardín"),
    ("401", RoomType.DOBLE, 2, 82000, 4, "Habitación doble de lujo"),
    ("402", RoomType.DOBLE, 2, 80000, 4, "Habitación doble con terraza"),
    ("403", RoomType.DOBLE, 3, 83000, 4, "Habitación doble superior"),
    ("404", RoomType.DOBLE, 2, 79000, 4, "Habitación doble luminosa, piso 4"),
    ("405", RoomType.DOBLE, 4, 88000, 4, "Habitación doble familiar grande"),
    ("406", RoomType.DOBLE, 2, 81000, 4, "Habitación doble renovada"),
    ("407", RoomType.DOBLE, 2, 80000, 4, "Habitación doble estándar"),
    ("408", RoomType.DOBLE, 2, 82000, 4, "Habitación doble con bañera jacuzzi"),
    # Suite (12 habitaciones) — Piso 5 y 6
    ("501", RoomType.SUITE, 2, 150000, 5, "Suite estándar con sala de estar"),
    ("502", RoomType.SUITE, 3, 160000, 5, "Suite con vista panorámica"),
    ("503", RoomType.SUITE, 2, 155000, 5, "Suite romántica con jacuzzi"),
    ("504", RoomType.SUITE, 4, 180000, 5, "Suite familiar"),
    ("505", RoomType.SUITE, 2, 158000, 5, "Suite ejecutiva"),
    ("506", RoomType.SUITE, 2, 162000, 5, "Suite deluxe"),
    ("507", RoomType.SUITE, 3, 170000, 5, "Suite premium con terraza"),
    ("601", RoomType.SUITE, 2, 165000, 6, "Suite superior con vista al mar"),
    ("602", RoomType.SUITE, 2, 168000, 6, "Suite de lujo"),
    ("603", RoomType.SUITE, 4, 190000, 6, "Suite familiar de lujo"),
    ("604", RoomType.SUITE, 2, 172000, 6, "Suite penthouse junior"),
    ("605", RoomType.SUITE, 3, 175000, 6, "Suite con salon privado"),
    # Presidencial (8 habitaciones) — Piso 7 (Penthouse)
    ("701", RoomType.PRESIDENCIAL, 2, 350000, 7, "Suite Presidencial con sala y comedor"),
    ("702", RoomType.PRESIDENCIAL, 4, 420000, 7, "Suite Presidencial familiar"),
    ("703", RoomType.PRESIDENCIAL, 2, 380000, 7, "Penthouse con terraza privada"),
    ("704", RoomType.PRESIDENCIAL, 6, 500000, 7, "Suite Presidencial Gran Lujo"),
    ("705", RoomType.PRESIDENCIAL, 2, 360000, 7, "Suite Presidencial Clásica"),
    ("706", RoomType.PRESIDENCIAL, 4, 440000, 7, "Suite Presidencial con jacuzzi exterior"),
    ("707", RoomType.PRESIDENCIAL, 2, 370000, 7, "Suite Presidencial con piano"),
    ("708", RoomType.PRESIDENCIAL, 8, 580000, 7, "Penthouse Royal — planta completa"),
]


async def run_seed() -> None:
    """Inserta los datos de prueba si la colección de huéspedes está vacía."""
    existing_guests = await Guest.find_all().count()
    if existing_guests > 0:
        logger.info("🌱 Seed omitido — ya existen %d huéspedes en la BD.", existing_guests)
        return

    logger.info("🌱 Ejecutando seed de datos de prueba...")

    # ── 1. Crear Huéspedes ──────────────────────────────────────────────────
    guests: list[Guest] = []
    for first, last, email, doc_num, doc_type, nationality in GUESTS_DATA:
        g = Guest(
            first_name=first,
            last_name=last,
            email=email,
            document_type=doc_type,
            document_number=doc_num,
            nationality=nationality,
            phone=f"+56 9 {hash(email) % 90000000 + 10000000}",
        )
        await g.insert()
        guests.append(g)
    logger.info("  ✅ %d huéspedes creados.", len(guests))

    # ── 2. Crear Habitaciones ───────────────────────────────────────────────
    rooms: list[Room] = []
    for num, rtype, cap, price, floor, desc in ROOMS_DATA:
        r = Room(
            number=num,
            room_type=rtype,
            capacity=cap,
            price_per_night=price,
            floor=floor,
            description=desc,
            state=RoomState.DISPONIBLE,
        )
        await r.insert()
        rooms.append(r)
    logger.info("  ✅ %d habitaciones creadas.", len(rooms))

    # ── 3. Crear Reservas variadas ──────────────────────────────────────────
    today = datetime.now(timezone.utc).date()
    reservations_created = 0

    # Reservas COMPLETADAS (pasadas)
    past_combos = [
        (0, 0, -60, -55),   # guest[0], room[0], hace 60 días
        (1, 1, -45, -42),
        (2, 2, -30, -28),
        (3, 15, -20, -17),
        (4, 16, -15, -12),
        (5, 30, -25, -22),
        (6, 31, -40, -36),
        (7, 40, -50, -47),
        (8, 45, -35, -31),
        (9, 3,  -10, -7),
        (10, 17, -55, -50),
        (11, 32, -22, -19),
    ]
    for gi, ri, d_in, d_out in past_combos:
        ci = today + timedelta(days=d_in)
        co = today + timedelta(days=d_out)
        nights = (co - ci).days
        res = Reservation(
            guest_id=guests[gi].id,
            room_id=rooms[ri].id,
            check_in=ci,
            check_out=co,
            status=ReservationStatus.COMPLETADA,
            total_price=nights * rooms[ri].price_per_night,
        )
        await res.insert()
        reservations_created += 1

    # Reservas CONFIRMADAS (activas — algunos check-in pasado = huéspedes actualmente en el hotel)
    active_combos = [
        (12, 4, -2, 3),    # ya ingresó, sale en 3 días
        (13, 5, -1, 4),
        (14, 18, 0, 5),    # check-in hoy
        (15, 19, 1, 4),    # check-in mañana
        (16, 33, 2, 6),
        (17, 34, 3, 7),
        (18, 41, 5, 10),
        (19, 42, 7, 12),
        (0, 6, 10, 14),    # guest[0] segunda reserva en el futuro
        (1, 20, 15, 18),
        (2, 35, 20, 25),
        (3, 43, 30, 35),
        (4, 7,  8, 11),
        (5, 21, 12, 15),
        (6, 36, 18, 22),
        (7, 44, 25, 30),
    ]
    for gi, ri, d_in, d_out in active_combos:
        ci = today + timedelta(days=d_in)
        co = today + timedelta(days=d_out)
        nights = (co - ci).days
        # Marcar habitación como OCUPADA si check-in ya pasó
        if ci <= today:
            await rooms[ri].set({Room.state: RoomState.OCUPADA})
        res = Reservation(
            guest_id=guests[gi].id,
            room_id=rooms[ri].id,
            check_in=ci,
            check_out=co,
            status=ReservationStatus.CONFIRMADA,
            total_price=nights * rooms[ri].price_per_night,
        )
        await res.insert()
        reservations_created += 1

    # Reservas CANCELADAS
    cancelled_combos = [
        (8, 8, -5, -2),
        (9, 22, 5, 8),
        (10, 37, 12, 15),
        (11, 46, 20, 25),
        (12, 9, -15, -10),
        (13, 23, 3, 6),
    ]
    for gi, ri, d_in, d_out in cancelled_combos:
        ci = today + timedelta(days=d_in)
        co = today + timedelta(days=d_out)
        nights = abs((co - ci).days)
        res = Reservation(
            guest_id=guests[gi].id,
            room_id=rooms[ri].id,
            check_in=ci,
            check_out=co,
            status=ReservationStatus.CANCELADA,
            total_price=nights * rooms[ri].price_per_night,
        )
        await res.insert()
        reservations_created += 1

    # Poner algunas habitaciones en mantenimiento
    for idx in [10, 25, 48]:
        await rooms[idx].set({Room.state: RoomState.MANTENIMIENTO})

    logger.info("  ✅ %d reservas creadas.", reservations_created)
    logger.info("🌱 Seed completado exitosamente.")
