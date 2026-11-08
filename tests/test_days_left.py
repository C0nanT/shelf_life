from datetime import timedelta

from tests.base import ApiTestCase


class DaysLeftTests(ApiTestCase):
    def on(self, days):
        return (self.today + timedelta(days=days)).isoformat()

    def page(self):
        return self.client.get("/").get_data(as_text=True)

    def test_api_reports_days_left_and_none_without_expiry(self):
        self.buy("Rice", "1", "unit", self.on(12))
        self.buy("Salt", "1", "unit", "")
        by_name = {p["name"]: p for p in self.list_purchases()}
        self.assertEqual(by_name["Rice"]["days_left"], 12)
        self.assertIsNone(by_name["Salt"]["days_left"])

    def test_bar_colour_follows_the_30_and_7_day_thresholds(self):
        cases = {31: "green", 30: "yellow", 8: "yellow", 7: "red", 0: "red", -1: "expired"}
        for days, colour in cases.items():
            self.buy(f"Item {days}", "1", "unit", self.on(days))
        html = self.page()
        for days, colour in cases.items():
            row = html.split(f"<td>Item {days}</td>")[1].split("</tr>")[0]
            self.assertIn(f'class="bar {colour}"', row, f"{days} days left")

    def test_label_shows_days_inside_the_bar(self):
        self.buy("Rice", "1", "unit", self.on(45))
        self.buy("Milk", "1", "unit", self.on(1))
        self.buy("Pasta", "1", "unit", self.on(0))
        self.buy("Cream", "1", "unit", self.on(-3))
        html = self.page()
        self.assertIn('<span class="bar-label">45 days</span>', html)
        self.assertIn('<span class="bar-label">1 day</span>', html)
        self.assertIn('<span class="bar-label">today</span>', html)
        self.assertIn('<span class="bar-label">expired 3d ago</span>', html)

    def test_no_bar_without_expiry(self):
        self.buy("Salt", "1", "unit", "")
        self.assertNotIn('class="bar', self.page())

    def test_bar_length_is_the_share_of_shelf_life_left(self):
        self.buy("Rice", "1", "unit", self.on(100))
        self.assertIn("width: 100%", self.page())  # bought today: full
        self.today += timedelta(days=75)  # 25 of 100 days left
        self.assertIn("width: 25%", self.page())
