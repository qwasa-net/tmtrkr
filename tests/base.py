"""."""

import logging

import tmtrkr.models

# set up logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


class DataBaseTestMixin:
    """Database models tests helper."""

    def setUp(self):
        """Init database -- create all tables."""
        tmtrkr.models.create_all()  # TODO: use alembic migrations here
        self.db = next(tmtrkr.models.db_session())
        super().setUp()

    def tearDown(self):
        """Close database -- drop all tables."""
        tmtrkr.models.drop_all()
        super().tearDown()
