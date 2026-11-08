import os
import tempfile
import unittest
from datetime import date

from shelf_life import create_app


class ApiTestCase(unittest.TestCase):
    """Base case: Flask test client over a temporary database and a fixed clock."""

    today = date(2026, 11, 8)

    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        self.app = create_app(
            {"TESTING": True, "DATABASE": self.db_path, "CLOCK": lambda: self.today}
        )
        self.client = self.app.test_client()

    def tearDown(self):
        os.unlink(self.db_path)

    def buy(self, name="Rice", quantity="1", unit="kg", expiry="", group="Pantry"):
        return self.client.post(
            "/api/purchases",
            json={
                "name": name,
                "quantity": quantity,
                "unit": unit,
                "expiry": expiry,
                "group": group,
            },
        )

    def list_purchases(self):
        return self.client.get("/api/purchases").get_json()
