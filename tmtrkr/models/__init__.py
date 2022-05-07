from .db import db_session, db_connection
from .records import Record
from .users import User
from .base import Base


def create_all():
    """Create tables for all models."""
    with db_connection() as connection:
        Base.metadata.create_all(bind=connection)


def drop_all():
    """Drop all tables."""
    with db_connection() as connection:
        Base.metadata.drop_all(bind=connection)
