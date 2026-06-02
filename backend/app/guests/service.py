"""
guests/service.py — Lógica de negocio del módulo de Huéspedes.

Responsabilidades:
  - Orquestar llamadas al repositorio.
  - Aplicar validaciones de negocio (unicidad, estado activo, etc.).
  - Convertir modelos Beanie a DTOs de respuesta.
  - Lanzar HTTPException con códigos semánticos correctos.

El servicio NO accede directamente a MongoDB — solo habla con GuestRepository.
"""

from __future__ import annotations

import math
from typing import Optional

from fastapi import HTTPException, status

from app.guests.model import Guest
from app.guests.repository import GuestRepository
from app.guests.schemas import (
    GuestCreate,
    GuestListResponse,
    GuestResponse,
    GuestUpdate,
)


class GuestService:
    """Servicio que gestiona todas las operaciones de negocio sobre Huéspedes."""

    def __init__(self) -> None:
        self.repo = GuestRepository()

    # ------------------------------------------------------------------
    # Helpers privados
    # ------------------------------------------------------------------

    def _to_response(self, guest: Guest) -> GuestResponse:
        """Convierte un documento Beanie en el DTO de respuesta de la API."""
        data = guest.model_dump(exclude={"revision_id"})
        data["id"] = str(guest.id)
        return GuestResponse(**data)

    async def _get_or_404(self, id: str) -> Guest:
        """Obtiene un huésped por id o lanza 404 si no existe."""
        guest = await self.repo.find_by_id(id)
        if not guest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Huésped con id '{id}' no encontrado.",
            )
        return guest

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    async def create_guest(self, data: GuestCreate) -> GuestResponse:
        """
        Registra un nuevo huésped.

        Validaciones:
          - Email único en la colección.
          - Número de documento único en la colección.
        """
        # Verificar unicidad de email
        if await self.repo.find_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un huésped registrado con el email '{data.email}'.",
            )

        # Verificar unicidad de documento
        if await self.repo.find_by_document_number(data.document_number):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un huésped con el documento '{data.document_number}'.",
            )

        guest = await self.repo.create(data.model_dump())
        return self._to_response(guest)

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------

    async def get_guest(self, id: str) -> GuestResponse:
        """Obtiene los datos de un huésped por su id."""
        guest = await self._get_or_404(id)
        return self._to_response(guest)

    async def list_guests(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        include_inactive: bool = False,
    ) -> GuestListResponse:
        """
        Lista huéspedes con paginación y búsqueda opcional.

        Args:
            page:             Página actual (base 1).
            size:             Registros por página (máx. 100).
            search:           Texto libre — busca en nombre, email, documento.
            include_inactive: Si True, incluye huéspedes desactivados.
        """
        skip = (page - 1) * size
        active_only = not include_inactive

        guests, total = await self.repo.search(
            query=search,
            skip=skip,
            limit=size,
            active_only=active_only,
        )

        pages = math.ceil(total / size) if size > 0 else 0

        return GuestListResponse(
            items=[self._to_response(g) for g in guests],
            total=total,
            page=page,
            size=size,
            pages=pages,
        )

    # ------------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------------

    async def update_guest(self, id: str, data: GuestUpdate) -> GuestResponse:
        """
        Actualización parcial de un huésped (PATCH).

        Validaciones:
          - El huésped debe existir.
          - Si cambia el email → debe ser único.
          - Si cambia el documento → debe ser único.
        """
        guest = await self._get_or_404(id)
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            # Nada que actualizar — devolvemos el estado actual
            return self._to_response(guest)

        # Validar unicidad de email si se está cambiando
        new_email = update_data.get("email")
        if new_email and new_email != guest.email:
            existing = await self.repo.find_by_email(new_email)
            if existing and str(existing.id) != id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"El email '{new_email}' ya está en uso por otro huésped.",
                )

        # Validar unicidad de documento si se está cambiando
        new_doc = update_data.get("document_number")
        if new_doc and new_doc != guest.document_number:
            existing = await self.repo.find_by_document_number(new_doc)
            if existing and str(existing.id) != id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"El documento '{new_doc}' ya está en uso por otro huésped.",
                )

        updated = await self.repo.update(guest, update_data)
        return self._to_response(updated)

    # ------------------------------------------------------------------
    # DELETE (soft)
    # ------------------------------------------------------------------

    async def delete_guest(self, id: str) -> dict:
        """
        Desactiva un huésped (soft-delete).
        El registro permanece en la BD para conservar el historial de reservas.
        """
        guest = await self._get_or_404(id)

        if not guest.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El huésped ya se encuentra inactivo.",
            )

        await self.repo.soft_delete(guest)
        return {
            "message": (
                f"Huésped '{guest.first_name} {guest.last_name}' "
                "desactivado correctamente."
            ),
            "id": id,
        }

    # ------------------------------------------------------------------
    # RELACIONES FUTURAS — preparado para Paso 3 (Bookings)
    # ------------------------------------------------------------------

    async def get_guest_bookings(self, id: str) -> list:
        """
        Devuelve las reservas asociadas a un huésped.

        ── Estado actual ──────────────────────────────────────────────
        Retorna lista vacía hasta que BookingRepository esté disponible.

        ── Implementación futura (descomentar en Paso 3) ──────────────
        # from app.bookings.repository import BookingRepository
        # await self._get_or_404(id)   # valida que el huésped existe
        # return await BookingRepository().find_by_guest_id(id)
        """
        await self._get_or_404(id)  # valida que el huésped existe → 404 si no
        return []
