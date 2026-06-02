"""
database.py — Gestión del ciclo de vida de la conexión a MongoDB mediante Beanie ODM.

Beanie es un ODM async construido sobre Motor que integra Pydantic v2 directamente.
Ventajas sobre Motor puro:
  - Modelos como clases Python (hereden de Document) con validación Pydantic.
  - Operaciones CRUD expresivas sin escribir queries en crudo.
  - Soporte nativo para índices, relaciones y migraciones ligeras.

Flujo:
  1. Al arrancar FastAPI (lifespan startup) → init_db() crea el AsyncIOMotorClient
     y registra los documentos Beanie con la base de datos.
  2. Al apagar FastAPI (lifespan shutdown) → close_db() cierra el cliente.

Uso desde servicios / routers:
    # No necesitas importar get_database() — Beanie gestiona la conexión internamente.
    # Solo importas tu Document y operas directamente:
    #   await Guest.find_all().to_list()
    #   await Guest(first_name="Ana", ...).insert()
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings

logger = logging.getLogger(__name__)

# Referencia global al cliente (útil para el endpoint /db-test)
_client: AsyncIOMotorClient | None = None


async def init_db(document_models: list) -> None:
    """
    Inicializa Beanie con el cliente Motor y los modelos Document registrados.

    Args:
        document_models: lista de clases que heredan de beanie.Document.
                         Se pasa desde main.py para evitar imports circulares.
    """
    global _client

    logger.info("Conectando a MongoDB en %s:%s …", settings.mongo_host, settings.mongo_port)

    _client = AsyncIOMotorClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=5_000,
    )

    await init_beanie(
        database=_client[settings.mongo_db_name],
        document_models=document_models,
    )

    # Verificación real de conectividad
    await _client.admin.command("ping")
    logger.info(
        "✅  Beanie inicializado — base de datos: '%s' | modelos: %s",
        settings.mongo_db_name,
        [m.__name__ for m in document_models],
    )


async def close_db() -> None:
    """Cierra el cliente Motor al apagar la aplicación."""
    global _client
    if _client:
        _client.close()
        logger.info("🔌  Conexión a MongoDB cerrada.")


async def get_client() -> AsyncIOMotorClient:
    """Retorna el cliente Motor activo (para operaciones de bajo nivel como listar colecciones)."""
    if _client is None:
        raise RuntimeError("La base de datos no está inicializada.")
    return _client
