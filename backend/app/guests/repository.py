"""
guests/repository.py — Repositorio específico del dominio de Huéspedes.

Hereda las operaciones CRUD genéricas de BaseRepository y agrega
métodos de consulta propios del dominio (búsqueda por email, documento, texto).
"""

from __future__ import annotations

import re
from typing import Optional

from app.guests.model import Guest
from app.shared.base_repository import BaseRepository


class GuestRepository(BaseRepository[Guest]):
    """Repositorio de acceso a datos para la colección 'guests'."""

    def __init__(self) -> None:
        super().__init__(Guest)

    # ------------------------------------------------------------------
    # Búsquedas por unicidad (usadas en validaciones del servicio)
    # ------------------------------------------------------------------

    async def find_by_email(self, email: str) -> Optional[Guest]:
        """Busca un huésped por su dirección de email (sin importar mayúsculas)."""
        return await Guest.find_one(
            Guest.email == email.lower().strip()
        )

    async def find_by_document_number(self, document_number: str) -> Optional[Guest]:
        """Busca un huésped por su número de documento (normalizado a mayúsculas)."""
        return await Guest.find_one(
            Guest.document_number == document_number.strip().upper()
        )

    # ------------------------------------------------------------------
    # Búsqueda paginada con filtros (usada en el listado)
    # ------------------------------------------------------------------

    async def search(
        self,
        query: Optional[str],
        skip: int,
        limit: int,
        active_only: bool,
    ) -> tuple[list[Guest], int]:
        """
        Devuelve una tupla (resultados, total) aplicando:
          - Filtro de activos/inactivos.
          - Búsqueda por texto sobre nombre, email y documento (regex case-insensitive).

        Args:
            query:       Texto libre de búsqueda (None = sin filtro de texto).
            skip:        Documentos a saltar (paginación).
            limit:       Máximo de documentos a devolver.
            active_only: Si True, excluye los huéspedes con is_active=False.

        Returns:
            Tupla (lista de guests, total de coincidencias).
        """
        filters: dict = {}

        if active_only:
            filters["is_active"] = True

        if query and query.strip():
            pattern = re.compile(re.escape(query.strip()), re.IGNORECASE)
            filters["$or"] = [
                {"first_name": {"$regex": pattern}},
                {"last_name": {"$regex": pattern}},
                {"email": {"$regex": pattern}},
                {"document_number": {"$regex": pattern}},
                {"nationality": {"$regex": pattern}},
            ]

        results = await self.find_all(skip=skip, limit=limit, filters=filters)
        total = await self.count(filters=filters)
        return results, total
