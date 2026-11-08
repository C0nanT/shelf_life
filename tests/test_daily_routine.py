import os
import tempfile
from datetime import timedelta
from unittest import mock

from shelf_life import daily_routine, telegram
from tests.base import ApiTestCase


class FakeSender:
    def __init__(self, fail=False):
        self.messages = []
        self.fail = fail

    def send(self, text):
        if self.fail:
            raise RuntimeError("telegram down")
        self.messages.append(text)


class MainWithoutTelegramTests(ApiTestCase):
    def test_backup_still_runs_and_exit_is_nonzero_without_telegram_env(self):
        with tempfile.TemporaryDirectory() as backup_dir:
            env = {"SHELF_LIFE_DB": self.db_path, "SHELF_LIFE_BACKUP_DIR": backup_dir}
            with mock.patch.dict(os.environ, env, clear=True):
                with self.assertRaises(SystemExit) as cm:
                    daily_routine.main()
            self.assertNotEqual(cm.exception.code, 0)
            self.assertTrue(os.listdir(backup_dir))


class DailyRoutineTests(ApiTestCase):
    def on(self, days_from_today):
        return (self.today + timedelta(days=days_from_today)).isoformat()

    def run_day(self, offset=0, sender=None):
        sender = sender or FakeSender()
        daily_routine.run(self.today + timedelta(days=offset), sender, self.db_path)
        return sender

    def pid(self, **kw):
        return self.buy(**kw).get_json()["id"]

    def test_digest_is_one_message_starting_with_stock_with_real_days(self):
        self.buy("Rice", "1", "kg", self.on(7), "Pantry")
        self.buy("Beans", "1", "kg", self.on(30), "Reserve")
        sender = self.run_day()
        self.assertEqual(len(sender.messages), 1)
        text = sender.messages[0]
        self.assertTrue(text.startswith("Stock"))
        self.assertIn("Rice", text)
        self.assertIn("7 days left", text)
        self.assertIn("Beans", text)
        self.assertIn("30 days left", text)

    def test_nothing_sent_without_new_milestone(self):
        self.buy("Rice", "1", "kg", self.on(20), "Pantry")
        self.assertEqual(self.run_day().messages, [])

    def test_running_again_does_not_duplicate(self):
        self.buy("Rice", "1", "kg", self.on(7), "Pantry")
        self.assertEqual(len(self.run_day().messages), 1)
        self.assertEqual(self.run_day().messages, [])

    def test_item_inside_warning_period_enters_once_then_follows_milestones(self):
        self.buy("Rice", "1", "kg", self.on(4), "Pantry")
        first = self.run_day()
        self.assertIn("4 days left", first.messages[0])
        self.assertEqual(self.run_day(1).messages, [])
        self.assertIn("expires today", self.run_day(4).messages[0])

    def test_long_gap_shows_item_once_with_latest_milestone(self):
        self.buy("Rice", "1", "kg", self.on(100), "Reserve")
        self.assertEqual(len(self.run_day(10).messages), 1)  # 90 days left
        sender = self.run_day(95)  # 5 days left, skipped 30 and 7
        self.assertEqual(len(sender.messages), 1)
        self.assertEqual(sender.messages[0].count("Rice"), 1)
        self.assertIn("5 days left", sender.messages[0])
        self.assertEqual(self.run_day(96).messages, [])

    def test_item_expired_when_recorded_enters_once(self):
        self.buy("Milk", "1", "L", self.on(-3), "Pantry")
        sender = self.run_day()
        self.assertIn("expired 3 days ago", sender.messages[0])
        self.assertEqual(self.run_day(1).messages, [])
        self.assertEqual(self.run_day(30).messages, [])

    def test_no_new_warning_after_milestone_zero(self):
        self.buy("Rice", "1", "kg", self.on(0), "Pantry")
        self.assertEqual(len(self.run_day().messages), 1)
        self.assertEqual(self.run_day(5).messages, [])

    def test_no_expiry_or_zero_balance_never_warns(self):
        self.buy("Salt", "1", "kg", "", "Pantry")
        self.buy("Rice", "1", "kg", self.on(0), "Pantry")
        self.client.post("/api/removals", json={
            "name": "Rice", "quantity": "1", "unit": "kg", "reason": "used"})
        self.assertEqual(self.run_day().messages, [])

    def test_reserve_and_pantry_defaults(self):
        self.buy("Alpha", "1", "kg", self.on(90), "Reserve")
        self.buy("Bravo", "1", "kg", self.on(90), "Pantry")
        text = self.run_day().messages[0]
        self.assertIn("Alpha", text)
        self.assertNotIn("Bravo", text)

    def test_move_recalculates_but_partial_removal_does_not(self):
        pid = self.pid(name="Rice", quantity="2", unit="kg", expiry=self.on(7))
        self.assertEqual(len(self.run_day().messages), 1)
        self.client.post("/api/removals", json={
            "name": "Rice", "quantity": "1", "unit": "kg", "reason": "used"})
        self.assertEqual(self.run_day().messages, [])
        self.client.post(f"/api/purchases/{pid}/move", json={"group": "Reserve"})
        self.assertEqual(len(self.run_day().messages), 1)

    def test_partial_move_creates_unwarned_purchase(self):
        pid = self.pid(name="Rice", quantity="2", unit="kg", expiry=self.on(7))
        self.run_day()
        self.client.post(f"/api/purchases/{pid}/move",
                         json={"group": "Reserve", "quantity": "1", "unit": "kg"})
        self.assertEqual(self.run_day().messages[0].count("Rice"), 1)

    def test_expiry_edit_recalculates(self):
        pid = self.pid(name="Rice", quantity="1", unit="kg", expiry=self.on(7))
        self.run_day()
        self.client.patch(f"/api/purchases/{pid}", json={"expiry": self.on(0)})
        self.assertIn("expires today", self.run_day().messages[0])

    def test_send_failure_saves_nothing_and_retries(self):
        self.buy("Rice", "1", "kg", self.on(7), "Pantry")
        with self.assertLogs("shelf_life.daily_routine", level="ERROR"):
            self.run_day(sender=FakeSender(fail=True))
        self.assertEqual(len(self.run_day().messages), 1)

    def test_steps_after_send_run_even_if_sending_fails(self):
        self.buy("Rice", "1", "kg", self.on(7), "Pantry")
        ran = []
        with self.assertLogs("shelf_life.daily_routine", level="ERROR"):
            daily_routine.run(self.today, FakeSender(fail=True), self.db_path,
                              extra_steps=[lambda: ran.append("backup")])
        self.assertEqual(ran, ["backup"])


class TelegramConfigTests(ApiTestCase):
    def test_sender_reads_token_and_chat_from_env(self):
        env = {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_CHAT_ID": "42"}
        with mock.patch.dict(os.environ, env):
            sender = telegram.TelegramSender.from_env()
        self.assertEqual((sender.token, sender.chat_id), ("tok", "42"))

    def test_missing_config_is_an_error(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(telegram.TelegramConfigError):
                telegram.TelegramSender.from_env()
