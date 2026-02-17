from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all ORM models in the Extraction bounded context.

    Uses SQLAlchemy 2.0 style with DeclarativeBase for better type hints
    and modern Python features.
    """

    pass
