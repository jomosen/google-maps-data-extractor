"""
Database initialization module.

Creates all database tables from SQLAlchemy models.
"""
from sqlalchemy import create_engine
from shared.logging import get_logger

from .models.base import Base
from .models.campaign_model import CampaignModel
from .models.place_extraction_task_model import PlaceExtractionTaskModel
from .models.extracted_place_model import ExtractedPlaceModel
from .models.extracted_place_review_model import ExtractedPlaceReviewModel
from .models.website_enrichment_task_model import WebsitePlaceEnrichmentTaskModel


logger = get_logger(__name__)


def init_database(database_url: str) -> None:
    """
    Initialize database by creating all tables.
    
    Args:
        database_url: SQLAlchemy database URL (e.g., "sqlite:///data.db")
    
    This is safe to call multiple times - it will only create tables
    that don't exist yet.
    """
    logger.info("database_init_starting", database_url=database_url)
    
    engine = create_engine(database_url)
    
    # Create all tables from models
    Base.metadata.create_all(engine)
    
    logger.info("database_init_completed", tables=list(Base.metadata.tables.keys()))


if __name__ == "__main__":
    # Can be run standalone to initialize the database
    init_database("sqlite:///data.db")
