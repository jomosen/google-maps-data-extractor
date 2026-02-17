from abc import ABC, abstractmethod
from typing import Optional

from ..entities.campaign import Campaign
from ..value_objects.ids import CampaignId


class CampaignRepository(ABC):
    """
    Puerto de persistencia para el agregado Campaign.

    Este es un repositorio de DOMINIO para operaciones de ESCRITURA:
    - save (persistir agregado)
    - find_by_id (cargar agregado para modificacion)
    - delete (eliminar agregado)
    - increment_* (actualizaciones atomicas de contadores)

    Para operaciones de LECTURA (listar, filtrar, estadisticas),
    usar CampaignQueryRepositoryPort en la capa de aplicacion.
    """

    @abstractmethod
    def save(self, campaign: Campaign) -> None:
        """
        Persiste el agregado Campaign (insert o update).

        Incluye todas las entidades hijas (tasks).
        """
        ...

    @abstractmethod
    def find_by_id(self, campaign_id: CampaignId) -> Optional[Campaign]:
        """
        Carga el agregado Campaign para modificacion.

        Usar solo cuando se necesita modificar el agregado.
        Para lectura/display, usar CampaignQueryRepositoryPort.
        """
        ...

    @abstractmethod
    def delete(self, campaign_id: CampaignId) -> None:
        """
        Elimina el agregado y todas sus entidades hijas (cascade).
        """
        ...

    @abstractmethod
    def increment_completed(self, campaign_id: CampaignId) -> None:
        """
        Incrementa atomicamente el contador de tareas completadas.

        Usa UPDATE atomico para evitar race conditions.
        """
        ...

    @abstractmethod
    def increment_failed(self, campaign_id: CampaignId) -> None:
        """
        Incrementa atomicamente el contador de tareas fallidas.

        Usa UPDATE atomico para evitar race conditions.
        """
        ...
