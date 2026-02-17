from enum import Enum


class EnrichmentType(Enum):
    """
    Tipos de enriquecimiento disponibles en el pipeline.

    Cada tipo representa un pool de workers que puede ejecutarse
    en paralelo con otros pools.

    Para añadir un nuevo tipo de enriquecimiento:
    1. Añadir el valor aquí
    2. Crear el WorkerService correspondiente
    3. Crear el TaskRepository correspondiente
    4. Registrar en el PipelineRunnerService
    5. Definir dependencias en EnrichmentPoolConfig si las tiene
    """
    WEBSITE = "website"      # Enriquecimiento desde el sitio web del place
    GBP = "gbp"              # Enriquecimiento desde Google Business Profile
    SOCIAL = "social"        # Enriquecimiento desde redes sociales
