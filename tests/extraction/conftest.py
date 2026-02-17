"""
Fixtures for extraction bounded context tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from extraction.infrastructure.persistence import Base, SqlAlchemyUnitOfWork


@pytest.fixture
def engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(engine):
    """Create a session factory bound to the test engine."""
    return sessionmaker(bind=engine)


@pytest.fixture
def uow(session_factory):
    """Create a Unit of Work for testing."""
    return SqlAlchemyUnitOfWork(session_factory)
