"""Database instance module."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import tmtrkr.settings

__all__ = ["db_session", "db_connection"]

engine = create_engine(tmtrkr.settings.DATABASE_URL, connect_args=tmtrkr.settings.DATABASE_CONNECT_ARGS)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def db_session():
    """Create a new databse session. Close it after usage."""
    try:
        db = Session()
        # print("yield", db)
        yield db
    finally:
        # print("close", db)
        db.close()


def db_connection():
    """Return database connction."""
    return engine.begin()
