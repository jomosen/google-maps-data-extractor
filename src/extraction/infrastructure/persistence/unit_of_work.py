from __future__ import annotations

from typing_extensions import Self

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ...domain.interfaces.unit_of_work import AbstractUnitOfWork
from .repositories.campaign_repository import SqlAlchemyCampaignRepository
from .repositories.extracted_place_repository import SqlAlchemyExtractedPlaceRepository
from .repositories.place_extraction_task_repository import (
    SqlAlchemyPlaceExtractionTaskRepository,
)
from .repositories.website_enrichment_task_repository import (
    SqlAlchemyWebsitePlaceEnrichmentTaskRepository,
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """
    SQLAlchemy implementation of the Unit of Work pattern.

    Manages database sessions and transactions, providing access to
    all repositories within a single transactional context.

    Usage:
        with uow:
            campaign = Campaign.create(...)
            uow.campaign_repository.save(campaign)
            uow.commit()
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("UnitOfWork not entered. Use 'with uow:' context.")
        return self._session

    @property
    def campaign_repository(self) -> SqlAlchemyCampaignRepository:
        return SqlAlchemyCampaignRepository(self.session)

    @property
    def extracted_place_repository(self) -> SqlAlchemyExtractedPlaceRepository:
        return SqlAlchemyExtractedPlaceRepository(self.session)

    @property
    def place_extraction_task_repository(self) -> SqlAlchemyPlaceExtractionTaskRepository:
        return SqlAlchemyPlaceExtractionTaskRepository(self.session)

    @property
    def website_enrichment_task_repository(self) -> SqlAlchemyWebsitePlaceEnrichmentTaskRepository:
        return SqlAlchemyWebsitePlaceEnrichmentTaskRepository(self.session)

    def commit(self) -> None:
        """Commits the current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rolls back the current transaction."""
        self.session.rollback()

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
        self.session.close()
        self._session = None


def create_unit_of_work(database_url: str) -> SqlAlchemyUnitOfWork:
    """
    Factory function to create a SqlAlchemyUnitOfWork.

    Args:
        database_url: SQLAlchemy database URL
            Examples:
            - sqlite:///./extraction.db
            - postgresql://user:pass@localhost/extraction

    Returns:
        Configured SqlAlchemyUnitOfWork instance.
    """
    engine = create_engine(database_url)
    session_factory = sessionmaker(bind=engine)
    return SqlAlchemyUnitOfWork(session_factory)
