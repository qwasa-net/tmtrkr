"""Database instance module."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import tmtrkr.settings

ALL = ["get_db"]

engine = create_engine(tmtrkr.settings.DATABASE_URL, connect_args=tmtrkr.settings.DATABASE_CONNECT_ARGS)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Create a new databse session. Close it after usage."""
    db = Session()
    try:
        yield db
    finally:
        db.close()
