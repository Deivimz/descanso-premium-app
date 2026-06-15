"""
main.py — Punto de entrada de la aplicación FastAPI.

Ciclo de vida (lifespan):
  - Startup : inicializa Beanie ODM con la lista de Document models.
  - Shutdown: cierra el cliente Motor limpiamente.

Por ahora la lista de document_models está vacía; se irá llenando
a medida que creemos los modelos Beanie en el Paso 2.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, close_db, get_client

# ── Módulos ───────────────────────────────────────────────────────────────────
# Modelos Beanie (se registran en init_db)
from app.guests.model import Guest
from app.users.model import User, Role
from app.rooms.model import Room
from app.reservations.model import Reservation

# Routers de cada módulo
from app.guests.router import router as guests_router
from app.users.router import router as users_router
from app.auth.router import router as auth_router
from app.rooms.router import router as rooms_router
from app.reservations.router import router as reservations_router
from app.dashboard.router import router as dashboard_router

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — gestiona Beanie + Motor
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ────────────────────────────────────────────────────────────
    # Agregar aquí los modelos Beanie de cada módulo conforme se implementen
    document_models = [
        Guest,
        User,
        Room,
        Reservation,
    ]
    await init_db(document_models)
    
    # ── Seed Admin User ────────────────────────────────────────────────────
    from app.users.repository import UserRepository
    from app.core.security import get_password_hash
    repo = UserRepository()
    admin = await repo.find_by_username("admin")
    if not admin:
        admin_user = User(
            username="admin",
            email="admin@descansopremium.com",
            rut="12345678-5",
            first_name="Admin",
            last_name="Sistema",
            hashed_password=get_password_hash("admin123"),
            role=Role.ADMIN,
            is_active=True
        )
        await repo.create(admin_user)
        logger.info("Admin user created (admin / admin123)")

    # ── Seed de Datos de Prueba ────────────────────────────────────────────
    from app.seed import run_seed
    await run_seed()

    yield
    # ── Shutdown ───────────────────────────────────────────────────────────
    await close_db()


# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    description="API de gestión para la cadena hotelera Descanso Premium.",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False,   # evita 307 en clientes que no siguen redirects
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers — cada módulo registra su propio router
# ---------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(guests_router)
app.include_router(rooms_router)
app.include_router(reservations_router)
app.include_router(dashboard_router)



# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------

@app.get("/ping", tags=["Health"])
async def ping():
    """Verifica que FastAPI está activo (sin tocar la BD)."""
    return {
        "status": "ok",
        "service": "descanso-premium-api",
        "environment": settings.environment,
    }


@app.get("/db-test", tags=["Health"])
async def db_test():
    """
    Prueba la conexión a MongoDB mediante Beanie/Motor.
    Devuelve información real de la base de datos:
      - Nombre de la BD
      - Lista de colecciones existentes
      - Resultado del comando serverStatus (versión de Mongo, uptime, etc.)
    """
    try:
        client = await get_client()
        db = client[settings.mongo_db_name]

        # Ping al servidor
        pong = await client.admin.command("ping")

        # Listar colecciones (estarán vacías hasta que insertemos el primer documento)
        collections = await db.list_collection_names()

        # Información del servidor
        server_info = await client.server_info()

        return {
            "status": "ok",
            "database": settings.mongo_db_name,
            "host": settings.mongo_host,
            "mongo_version": server_info.get("version", "desconocida"),
            "collections": collections,
            "ping_ok": pong.get("ok") == 1.0,
        }
    except Exception as exc:
        logger.error("db-test falló: %s", exc)
        raise HTTPException(status_code=503, detail=f"Error de conexión: {exc}")


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Bienvenido a Descanso Premium API. Visita /docs para la documentación."
    }
