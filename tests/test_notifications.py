"""Notification tests: what would reach Telegram, and when.

Driven through the daily routine with a fake sender and a simulated date,
plus end-to-end through `main()` with the HTTP call to Telegram mocked.
"""
import json
import os
import tempfile
import urllib.error
from datetime import date, timedelta
from unittest import mock

from shelf_life import daily_routine, telegram
from tests.base import ApiTestCase
from tests.test_daily_routine import FakeSender


class NotificationTestCase(ApiTestCase):
    def on(self, days_from_today):
        return (self.today + timedelta(days=days_from_today)).isoformat()

    def run_day(self, offset=0, sender=None):
        sender = sender or FakeSender()
        daily_routine.run(self.today + timedelta(days=offset), sender, self.db_path)
        return sender

    def days_with_messages(self, last_day):
        """Run the routine once per day from day 0 to `last_day`; return the
        days on which a message was sent, with its text."""
        sent = {}
        for offset in range(last_day + 1):
            sender = self.run_day(offset)
            self.assertLessEqual(len(sender.messages), 1, f"day {offset}")
            if sender.messages:
                sent[offset] = sender.messages[0]
        return sent


class TimelineTests(NotificationTestCase):
    def test_reserve_item_warns_at_30_7_and_0_days_only(self):
        self.buy("Rice", "1", "unit", self.on(45), "Reserve")
        sent = self.days_with_messages(60)
        self.assertEqual(sorted(sent), [15, 38, 45])  # 30, 7 and 0 days left
        self.assertIn("30 days left", sent[15])
        self.assertIn("7 days left", sent[38])
        self.assertIn("expires today", sent[45])

    def test_pantry_item_warns_at_7_and_0_days_only(self):
        self.buy("Milk", "1", "unit", self.on(20), "Pantry")
        sent = self.days_with_messages(30)
        self.assertEqual(sorted(sent), [13, 20])
        self.assertIn("7 days left", sent[13])
        self.assertIn("expires today", sent[20])

    def test_reserve_item_far_from_expiry_stays_silent(self):
        self.buy("Canned beans", "1", "unit", self.on(200), "Reserve")
        self.assertEqual(self.days_with_messages(160), {})

    def test_item_with_no_expiry_never_warns(self):
        self.buy("Salt", "1", "unit", "", "Reserve")
        self.assertEqual(self.days_with_messages(400), {})

    def test_month_only_expiry_counts_to_the_last_day_of_the_month(self):
        self.buy("Tuna", "1", "unit", "12/2026", "Pantry")  # valid through 31/12/2026
        sent = self.days_with_messages(60)
        last_day = (date(2026, 12, 31) - self.today).days
        self.assertEqual(sorted(sent), [last_day - 7, last_day])
        self.assertIn("31/12/2026", sent[last_day])

    def test_pc_off_for_weeks_gives_one_message_with_latest_milestone(self):
        self.buy("Rice", "1", "unit", self.on(45), "Reserve")
        self.run_day(15)  # 30 days left
        sender = self.run_day(44)  # PC was off: skipped 7 and the days between
        self.assertEqual(len(sender.messages), 1)
        self.assertIn("1 day left", sender.messages[0])
        self.assertEqual(self.run_day(45).messages[0].count("Rice"), 1)

    def test_expired_item_warns_once_then_stops(self):
        self.buy("Cream", "1", "unit", self.on(-2), "Reserve")
        sent = self.days_with_messages(30)
        self.assertEqual(list(sent), [0])
        self.assertIn("expired 2 days ago", sent[0])


class DigestTests(NotificationTestCase):
    def test_digest_text_is_exact_and_sorted_by_expiry(self):
        self.buy("Rice", "1", "unit", self.on(7), "Pantry")
        self.buy("Beans", "1", "unit", self.on(30), "Reserve")
        self.buy("Milk", "1", "unit", self.on(-1), "Pantry")
        self.buy("Pasta", "1", "unit", self.on(0), "Pantry")
        [text] = self.run_day().messages
        d = lambda n: (self.today + timedelta(days=n)).strftime("%d/%m/%Y")
        self.assertEqual(text, "\n".join([
            "Stock: expiry warnings",
            f"- Milk (Pantry): expired 1 day ago [{d(-1)}]",
            f"- Pasta (Pantry): expires today [{d(0)}]",
            f"- Rice (Pantry): 7 days left [{d(7)}]",
            f"- Beans (Reserve): 30 days left [{d(30)}]",
        ]))

    def test_many_items_still_make_a_single_message(self):
        for i in range(12):
            self.buy(f"Item {i}", "1", "unit", self.on(7), "Pantry")
        sender = self.run_day()
        self.assertEqual(len(sender.messages), 1)
        self.assertEqual(sender.messages[0].count("\n- "), 12)

    def test_only_items_reaching_a_milestone_today_are_listed(self):
        self.buy("Rice", "1", "unit", self.on(7), "Pantry")
        self.run_day()
        self.buy("Milk", "1", "unit", self.on(7), "Pantry")
        [text] = self.run_day().messages
        self.assertIn("Milk", text)
        self.assertNotIn("Rice", text)

    def test_days_use_singular_and_plural(self):
        self.buy("A", "1", "unit", self.on(-1), "Pantry")
        self.buy("B", "1", "unit", self.on(-5), "Pantry")
        [text] = self.run_day().messages
        self.assertIn("expired 1 day ago", text)
        self.assertIn("expired 5 days ago", text)


class FoodExceptionTests(NotificationTestCase):
    def food_id(self, name):
        foods = self.client.get("/api/foods/all").get_json()
        return next(f["id"] for f in foods if f["name"] == name)

    def test_food_exception_replaces_group_milestones_in_any_group(self):
        self.buy("Honey", "1", "unit", self.on(70), "Reserve")
        self.buy("Jam", "1", "unit", self.on(70), "Pantry")
        for name in ("Honey", "Jam"):
            self.client.patch(f"/api/foods/{self.food_id(name)}",
                              json={"milestones": "60,0"})
        sent = self.days_with_messages(70)
        self.assertEqual(sorted(sent), [10, 70])  # 60 days left and the expiry day
        self.assertIn("Honey", sent[10])
        self.assertIn("Jam", sent[10])

    def test_changing_milestones_warns_again_on_the_next_run(self):
        self.buy("Rice", "1", "unit", self.on(7), "Pantry")
        self.assertEqual(len(self.run_day().messages), 1)
        self.assertEqual(self.run_day().messages, [])
        self.client.patch(f"/api/foods/{self.food_id('Rice')}",
                          json={"milestones": "10,0"})
        self.assertIn("7 days left", self.run_day().messages[0])


class TelegramRequestTests(ApiTestCase):
    def fake_response(self, status=200):
        response = mock.MagicMock()
        response.status = status
        response.__enter__.return_value = response
        return response

    def test_sends_one_post_to_the_bot_api_with_chat_and_text(self):
        sender = telegram.TelegramSender("TOKEN123", "-100555")
        with mock.patch("urllib.request.urlopen",
                        return_value=self.fake_response()) as urlopen:
            sender.send("Stock: hello")
        [call] = urlopen.call_args_list
        request = call.args[0]
        self.assertEqual(request.full_url,
                         "https://api.telegram.org/botTOKEN123/sendMessage")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(json.loads(request.data),
                         {"chat_id": "-100555", "text": "Stock: hello"})

    def test_http_error_from_telegram_raises(self):
        sender = telegram.TelegramSender("bad", "1")
        error = urllib.error.HTTPError("url", 401, "Unauthorized", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaises(urllib.error.HTTPError):
                sender.send("x")

    def test_network_failure_raises(self):
        sender = telegram.TelegramSender("t", "1")
        with mock.patch("urllib.request.urlopen",
                        side_effect=urllib.error.URLError("offline")):
            with self.assertRaises(urllib.error.URLError):
                sender.send("x")


class MainEndToEndTests(ApiTestCase):
    """The real command, as the container runs it: env in, HTTP call mocked."""

    def setUp(self):
        super().setUp()
        self.backup_dir = tempfile.mkdtemp()
        self.env = {
            "SHELF_LIFE_DB": self.db_path,
            "SHELF_LIFE_BACKUP_DIR": self.backup_dir,
            "TELEGRAM_BOT_TOKEN": "tok",
            "TELEGRAM_CHAT_ID": "42",
        }

    def tearDown(self):
        for name in os.listdir(self.backup_dir):
            os.unlink(os.path.join(self.backup_dir, name))
        os.rmdir(self.backup_dir)
        super().tearDown()

    def run_main(self, urlopen):
        with mock.patch.dict(os.environ, self.env, clear=True), \
                mock.patch("urllib.request.urlopen", urlopen):
            with self.assertRaises(SystemExit) as cm:
                daily_routine.main()
        return cm.exception.code

    def ok(self):
        response = mock.MagicMock()
        response.status = 200
        response.__enter__.return_value = response
        return mock.MagicMock(return_value=response)

    def expiring_in(self, days):
        return (date.today() + timedelta(days=days)).isoformat()

    def test_due_item_is_sent_once_and_never_repeated(self):
        self.buy("Rice", "1", "unit", self.expiring_in(7), "Pantry")
        first = self.ok()
        self.assertEqual(self.run_main(first), 0)
        [call] = first.call_args_list
        body = json.loads(call.args[0].data)
        self.assertEqual(body["chat_id"], "42")
        self.assertTrue(body["text"].startswith("Stock"))
        self.assertIn("Rice", body["text"])
        second = self.ok()
        self.assertEqual(self.run_main(second), 0)
        second.assert_not_called()

    def test_nothing_due_sends_no_request(self):
        self.buy("Rice", "1", "unit", self.expiring_in(20), "Pantry")
        urlopen = self.ok()
        self.assertEqual(self.run_main(urlopen), 0)
        urlopen.assert_not_called()

    def test_telegram_failure_exits_nonzero_backs_up_and_retries_next_run(self):
        self.buy("Rice", "1", "unit", self.expiring_in(7), "Pantry")
        failing = mock.MagicMock(side_effect=urllib.error.URLError("offline"))
        with self.assertLogs("shelf_life.daily_routine", level="ERROR"):
            self.assertNotEqual(self.run_main(failing), 0)
        self.assertTrue(os.listdir(self.backup_dir))  # backup still ran
        retry = self.ok()
        self.assertEqual(self.run_main(retry), 0)
        self.assertEqual(retry.call_count, 1)  # the warning was not lost
