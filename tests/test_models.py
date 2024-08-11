"""Database models tests."""

import datetime
import unittest

from tmtrkr.models import Record, User

from .base import DataBaseTestMixin


class TestUsers(DataBaseTestMixin, unittest.TestCase):
    """Test User database model."""

    def test_create_user(self):
        """Create user."""
        user = User(name="username")
        user.save(session=self.db)
        self.assertTrue(user.id > 0)
        self.assertEqual(user.name, "username")


class TestRecords(DataBaseTestMixin, unittest.TestCase):
    """Test Record database model."""

    def test_create_record(self):
        """Create record."""
        user = User(name="username")
        user.save(session=self.db)
        start = datetime.datetime.now() - datetime.timedelta(hours=4)
        end = start - datetime.timedelta(hours=2)
        record = Record(user=user, name="record", start=start.timestamp(), end=end.timestamp())
        record.save(session=self.db)
        self.assertTrue(record.id > 0)
        self.assertEqual(record.name, "record")
        self.assertEqual(record.user.name, "username")
        self.assertEqual(record.duration, (end - start).total_seconds())


if __name__ == "__main__":
    unittest.main()
