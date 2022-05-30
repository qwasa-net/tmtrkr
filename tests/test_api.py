"""."""
import datetime
import random
import unittest

import tmtrkr.settings as settings
from fastapi.testclient import TestClient
from tmtrkr.api.api import app
from tmtrkr.models import Record

from .base import DataBaseTestMixin


class TestAPIUsers(DataBaseTestMixin, unittest.TestCase):
    """Test User database model."""

    def setUp(self):
        super().setUp()
        settings.AUTH_USERS_ALLOW_UNKNOWN = True
        self.client = TestClient(app)

    def test_404(self):
        """Get 404."""
        rsp = self.client.get(settings.API_BASE_PREFIX + "404.html")
        self.assertEqual(rsp.status_code, 404)

    def test_login(self):
        """Try /login."""
        rsp = self.client.get(settings.API_BASE_PREFIX + "/users/login")
        self.assertNotEqual(rsp.status_code, 404)

    def test_logout(self):
        """Try /logout."""
        rsp = self.client.get(settings.API_BASE_PREFIX + "/users/logout")
        self.assertNotEqual(rsp.status_code, 404)


class TestAPIRecords(DataBaseTestMixin, unittest.TestCase):
    """Test User database model."""

    def setUp(self):
        """."""
        super().setUp()
        settings.AUTH_USERS_ALLOW_UNKNOWN = True
        self.client = TestClient(app)

    def test_records_list(self, N=100):
        """Get records list."""
        self._create_records(N)
        rsp = self.client.get(settings.API_BASE_PREFIX + "/records/")
        self.assertEqual(rsp.status_code, 200)
        data = rsp.json()
        self.assertEqual(data["count"], N)
        self.assertEqual(len(data["records"]), N)
        self.assertTrue(data["duration"] > 0)
        self.assertTrue(data["duration"] % 60 == 0)

    def test_record_post(self):
        """Post new valid records."""
        records = [
            {"name": "new record #1", "start": 1577880000, "end": 1577883600, "tags": "demo test"},
            {"name": "new record #2", "start": 1577880000, "end": 1577883600},
            {"name": "new record #3", "start": 1577880000},
        ]
        for record in records:
            rsp = self.client.post(settings.API_BASE_PREFIX + "/records/", json=record)
            self.assertIn(rsp.status_code, [200, 201])
            data = rsp.json()
            self.assertTrue(data["id"] > 0)
            self.assertEqual(data["name"], record["name"])

    def test_record_post_invalid_times(self):
        """Post invalid record (end<start)."""
        record = {"name": "end<start", "start": 1577880000, "end": 1577872800}
        rsp = self.client.post(settings.API_BASE_PREFIX + "/records/", json=record)
        self.assertEqual(rsp.status_code, 422)

    def test_record_post_invalid_name(self):
        """Post invalid record (no name)."""
        record = {"start": 1577880000, "end": 1577872800}
        rsp = self.client.post(settings.API_BASE_PREFIX + "/records/", json=record)
        self.assertEqual(rsp.status_code, 422)

    def test_record_update(self):
        """Update record."""
        record = {"name": "record name", "start": 1580551200, "end": 1580562000}
        rsp1 = self.client.post(settings.API_BASE_PREFIX + "/records/", json=record)
        self.assertIn(rsp1.status_code, [200, 201, 202])
        posted = rsp1.json()
        posted["name"] = "record updated"
        posted["start"] -= 60 * 60
        posted["end"] += 60 * 60
        rsp2 = self.client.patch(settings.API_BASE_PREFIX + f"/records/{posted['id']}", json=posted)
        self.assertIn(rsp2.status_code, [200, 201, 202])
        rsp3 = self.client.get(settings.API_BASE_PREFIX + f"/records/{posted['id']}")
        self.assertIn(rsp3.status_code, [200, 201, 202])
        updated = rsp3.json()
        self.assertEqual(updated["name"], "record updated")
        self.assertEqual(updated["duration"], record["end"] - record["start"] + 2 * 60 * 60)

    def _create_records(self, N):
        h = 0
        start = (datetime.datetime.now()).replace(minute=0, second=0, microsecond=0)
        for i in range(N):
            h += random.randint(1, 10)
            start = start - datetime.timedelta(hours=h)
            end = start + datetime.timedelta(hours=0.25 * random.randint(1, 10))
            record = Record(name=f"record #{(i+1):03}", start=start.timestamp(), end=end.timestamp())
            record.save(session=self.db)
