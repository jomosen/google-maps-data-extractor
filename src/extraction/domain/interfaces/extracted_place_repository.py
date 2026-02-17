from abc import ABC, abstractmethod
from typing import Optional

from ..entities.extracted_place import ExtractedPlace
from ..value_objects.ids import PlaceId


class ExtractedPlaceRepository(ABC):
    """
    Puerto de persistencia para el agregado ExtractedPlace.

    Este es un repositorio de DOMINIO para operaciones de ESCRITURA:
    - save (persistir agregado con hijos)
    - find_by_place_id (cargar agregado para modificacion/enriquecimiento)
    - exists_by_place_id (verificar existencia para deduplicacion)

    Para operaciones de LECTURA (listar lugares, busqueda, estadisticas),
    usar PlaceQueryRepositoryPort en la capa de aplicacion.
    """

    @abstractmethod
    def save(self, place: ExtractedPlace) -> None:
        """
        Persiste el agregado ExtractedPlace con todas sus entidades hijas.

        Incluye:
        - Reviews
        - Booking options
        - Website enrichment (si presente)
        """
        ...

    @abstractmethod
    def find_by_place_id(self, place_id: PlaceId) -> Optional[ExtractedPlace]:
        """
        Carga el agregado para modificacion/enriquecimiento.

        Usar cuando se necesita agregar enrichment data al place.
        """
        ...

    @abstractmethod
    def exists_by_place_id(self, place_id: PlaceId) -> bool:
        """
        Verifica si existe un place con el ID dado.

        Usado para deduplicacion antes de guardar nuevos places.
        Mas eficiente que find_by_place_id cuando solo se necesita
        verificar existencia.
        """
        ...
