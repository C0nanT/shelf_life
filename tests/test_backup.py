import os
import sqlite3
import tempfile
from datetime import timedelta

from shelf_life import backup, daily_routine
from tests.base import ApiTestCase
from tests.test_daily_routine import FakeSender


class BackupTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dest = os.path.join(self._tmp.name, "nested", "backups")

    def back_up(self, offset=0):
        return backup.back_up(self.db_path, self.dest, self.today + timedelta(days=offset))

    def names(self):
        return sorted(os.listdir(self.dest))

    def test_copy_is_a_valid_database_with_the_data(self):
        self.buy("Rice", "2", "kg", "2027-01-01")
        path = self.back_up()
        conn = sqlite3.connect(path)
        try:
            self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM purchase").fetchone()[0], 1)
        finally:
            conn.close()

    def test_destination_folder_is_created(self):
        self.assertFalse(os.path.exists(self.dest))
        self.back_up()
        self.assertEqual(len(self.names()), 1)

    def test_several_runs_in_a_day_leave_one_copy_with_latest_data(self):
        self.back_up()
        self.buy("Rice", "2", "kg", "2027-01-01")
        self.back_up()
        self.assertEqual(len(self.names()), 1)
        conn = sqlite3.connect(os.path.join(self.dest, self.names()[0]))
        try:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM purchase").fetchone()[0], 1)
        finally:
            conn.close()

    def test_only_seven_most_recent_copies_are_kept(self):
        for day in range(10):
            self.back_up(day)
        self.assertEqual(len(self.names()), 7)
        self.assertEqual(self.names()[0], backup.file_name(self.today + timedelta(days=3)))

    def test_retention_leaves_other_files_alone(self):
        os.makedirs(self.dest)
        for name in ("notes.txt", "shelf_life-old.db", "other-2020-01-01.db"):
            open(os.path.join(self.dest, name), "w").close()
        for day in range(10):
            self.back_up(day)
        for name in ("notes.txt", "shelf_life-old.db", "other-2020-01-01.db"):
            self.assertIn(name, self.names())
        self.assertEqual(len(self.names()), 10)

    def test_backup_runs_even_if_telegram_fails(self):
        self.buy("Rice", "1", "kg", (self.today + timedelta(days=7)).isoformat())
        ok = daily_routine.run(self.today, FakeSender(fail=True), self.db_path,
                               backup_dir=self.dest)
        self.assertFalse(ok)
        self.assertEqual(len(self.names()), 1)
