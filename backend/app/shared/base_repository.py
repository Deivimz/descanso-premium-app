"""
shared/base_repository.py — Repositorio base genérico para Beanie ODM.

Cualquier módulo futuro (rooms, bookings, users…) hereda de esta clase
y obtiene las operaciones CRUD sin escribir una sola línea de acceso a BD.

Patrón de uso:
    class RoomRepository(BaseRepository[Room]):
        def __init__(self):
            super().__init__(Room)
        # Métodos específicos del dominio aquí…
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Generic, Optional, Type, TypeVar

from beanie import Document, PydanticObjectId

logger = logging.getLogger(__name__)

# T debe ser una subclase de Document (modelo Beanie)
T = TypeVar("T", bound=Document)


class BaseRepository(Generic[T]):
    """
    Repositorio base con operaciones CRUD genéricas sobre un Document Beanie.

    Args:
        model: Clase del Document Beanie que gestiona este repositorio.
    """

    def __init__(self, model: Type[T]) -> None:
        self.model = model

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    async def create(self, data: dict[str, Any] | T) -> T:
        """Crea e inserta un nuevo documento en la colección."""
        if isinstance(data, dict):
            instance = self.model(**data)
        else:
            instance = data
        return await instance.insert()

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------

    async def find_by_id(self, id: str) -> Optional[T]:
        """
        Busca un documento por su _id.
        Devuelve None si el id no es un ObjectId válido o no existe el documento.
        """
        try:
            obj_id = PydanticObjectId(id)
        except Exception:
            logger.warning("find_by_id: id inválido recibido → '%s'", id)
            return None
        return await self.model.get(obj_id)

    async def find_all(
        self,
        skip: int = 0,
        limit: int = 20,
        filters: dict[str, Any] | None = None,
    ) -> list[T]:
        """
        Devuelve una lista paginada de documentos que coincidan con los filtros.
        Los filtros usan la sintaxis de queries de MongoDB (diccionarios).
        """
        return (
            await self.model.find(filters or {})
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Cuenta los documentos que coincidan con los filtros dados."""
        return await self.model.find(filters or {}).count()

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    async def update(self, document: T, update_data: dict[str, Any]) -> T:
        """
        Aplica un diccionario de campos actualizados sobre un documento
        ya cargado y lo persiste. Actualiza automáticamente `updated_at`.

        Args:
            document: Instancia del Document ya recuperada de la BD.
            update_data: Campos a actualizar (solo los que cambian).
        """
        for field, value in update_data.items():
            setattr(document, field, value)
        document.updated_at = datetime.now(timezone.utc)  # type: ignore[attr-defined]
        await document.save()
        return document

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    async def soft_delete(self, document: T) -> T:
        """
        Desactiva un documento estableciendo is_active=False.
        El registro permanece en la BD para auditoría y referencias históricas.

        Requiere que el Document tenga el campo `is_active: bool`.
        """
        document.is_active = False  # type: ignore[attr-defined]
        document.updated_at = datetime.now(timezone.utc)  # type: ignore[attr-defined]
        await document.save()
        return document

    async def hard_delete(self, document: T) -> None:
        """Elimina físicamente el documento de la colección. Usar con cuidado."""
        await document.delete()
