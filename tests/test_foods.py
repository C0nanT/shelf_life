from datetime import timedelta

from shelf_life import daily_routine
from tests.base import ApiTestCase


class Sender:
    def __init__(self):
        self.messages = []

    def send(self, text):
        self.messages.append(text)


class FoodsTests(ApiTestCase):
    def foods(self):
        return self.client.get("/api/foods/all").get_json()

    def test_foods_report_purchase_count(self):
        self.buy("Rice")
        self.buy("Rice")
        self.buy("Beans")
        self.assertEqual({f["name"]: f["purchase_count"] for f in self.foods()},
                         {"Rice": 2, "Beans": 1})

    def food_id(self, name):
        return next(f["id"] for f in self.foods() if f["name"] == name)

    def patch(self, food, **fields):
        return self.client.patch(f"/api/foods/{self.food_id(food)}", json=fields)

    def history(self):
        return self.client.get("/api/removals").get_json()

    def on(self, days):
        return (self.today + timedelta(days=days)).isoformat()

    def run_day(self):
        sender = Sender()
        daily_routine.run(self.today, sender, self.db_path)
        return sender

    # rename
    def test_rename_to_unused_name_only_changes_name(self):
        self.buy("Riice", "1", "kg", "2027-01-01")
        self.assertEqual(self.patch("Riice", name="Rice").status_code, 200)
        self.assertEqual([f["name"] for f in self.foods()], ["Rice"])
        self.assertEqual(self.list_purchases()[0]["name"], "Rice")

    def test_rename_to_existing_name_asks_for_confirmation(self):
        self.buy("Riice", "1", "kg")
        self.buy("Rice", "2", "kg")
        r = self.patch("Riice", name="rice")
        self.assertEqual(r.status_code, 409)
        self.assertTrue(r.get_json()["needs_confirmation"])
        self.assertEqual(len(self.foods()), 2)

    def test_confirmed_merge_moves_purchases_and_history(self):
        self.buy("Riice", "3", "kg", "2027-01-01")
        self.buy("Rice", "2", "kg", "2027-02-01")
        self.client.post("/api/removals", json={
            "name": "Riice", "quantity": "1", "unit": "kg", "reason": "used"})
        r = self.patch("Riice", name="Rice", confirm_merge=True)
        self.assertEqual(r.status_code, 200)
        self.assertEqual([f["name"] for f in self.foods()], ["Rice"])
        self.assertEqual([(p["name"], p["quantity"]) for p in self.list_purchases()],
                         [("Rice", "2"), ("Rice", "2")])
        self.assertEqual([h["food"] for h in self.history()], ["Rice"])

    def test_merge_converts_within_family(self):
        self.buy("Riice", "500", "g")
        self.buy("Rice", "1", "kg")
        self.assertEqual(self.patch("Riice", name="Rice", confirm_merge=True).status_code, 200)
        self.assertEqual(sorted(p["quantity"] for p in self.list_purchases()), ["0.5", "1"])

    def test_merge_keeps_destination_milestones(self):
        self.buy("Riice", "1", "kg")
        self.buy("Rice", "1", "kg")
        self.patch("Riice", milestones="3")
        self.patch("Rice", milestones="30,7,0")
        self.patch("Riice", name="Rice", confirm_merge=True)
        self.assertEqual(self.foods()[0]["milestones"], "30,7,0")

    def test_merge_between_families_is_blocked(self):
        self.buy("Milk", "1", "L")
        self.buy("Milkk", "1", "kg")
        r = self.patch("Milkk", name="Milk", confirm_merge=True)
        self.assertEqual(r.status_code, 400)
        self.assertEqual(len(self.foods()), 2)

    def test_family_mismatch_blocked_even_before_confirmation(self):
        self.buy("Milk", "1", "L")
        self.buy("Milkk", "1", "kg")
        self.assertEqual(self.patch("Milkk", name="Milk").status_code, 400)

    # unit
    def test_unit_family_change_blocked_with_purchases(self):
        self.buy("Rice", "1", "kg")
        self.assertEqual(self.patch("Rice", unit="L").status_code, 400)
        self.assertEqual(self.foods()[0]["unit"], "kg")

    def test_unit_change_within_family_converts_quantities(self):
        self.buy("Rice", "1.5", "kg")
        self.assertEqual(self.patch("Rice", unit="g").status_code, 200)
        p = self.list_purchases()[0]
        self.assertEqual((p["quantity"], p["unit"]), ("1500", "g"))

    def test_unit_family_change_allowed_without_purchases(self):
        self.buy("Rice", "1", "kg")
        pid = self.list_purchases()[0]["id"]
        self.client.delete(f"/api/purchases/{pid}")
        self.assertEqual(self.patch("Rice", unit="L").status_code, 200)

    # milestones
    def test_name_and_unit_only_are_enough(self):
        self.buy("Rice", "1", "kg")
        self.assertEqual(self.patch("Rice", name="Rice", unit="kg").status_code, 200)
        self.assertEqual(self.foods()[0]["milestones"], "")

    def test_invalid_milestones_rejected(self):
        self.buy("Rice", "1", "kg")
        self.assertEqual(self.patch("Rice", milestones="a,b").status_code, 400)
        self.assertEqual(self.patch("Rice", milestones="-1").status_code, 400)

    def test_milestones_are_stored_normalized(self):
        self.buy("Rice", "1", "kg")
        self.patch("Rice", milestones=" 7, 30 ,0")
        self.assertEqual(self.foods()[0]["milestones"], "30,7,0")

    def test_exception_milestones_replace_group_milestones(self):
        # Reserve default would warn at 90 days; exception only at 10 and 0.
        self.buy("Beans", "1", "kg", self.on(60), "Reserve")
        self.patch("Beans", milestones="10,0")
        self.assertEqual(self.run_day().messages, [])

    def test_exception_applies_in_pantry_too(self):
        self.buy("Rice", "1", "kg", self.on(20), "Pantry")
        self.patch("Rice", milestones="30,0")
        self.assertEqual(len(self.run_day().messages), 1)

    def test_changing_milestones_recalculates_warnings(self):
        self.buy("Rice", "1", "kg", self.on(7), "Pantry")
        self.assertEqual(len(self.run_day().messages), 1)
        self.assertEqual(self.run_day().messages, [])
        self.patch("Rice", milestones="7,0")
        self.assertEqual(len(self.run_day().messages), 1)

    def test_foods_page_renders(self):
        self.buy("Rice", "1", "kg")
        r = self.client.get("/foods")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"Rice", r.data)

    def test_form_rename_requires_confirmation_then_merges(self):
        self.buy("Riice", "1", "kg")
        self.buy("Rice", "1", "kg")
        fid = self.food_id("Riice")
        r = self.client.post(f"/foods/{fid}", data={"name": "Rice", "unit": "kg"})
        self.assertIn(b"Merge", r.data)
        self.assertEqual(len(self.foods()), 2)
        self.client.post(f"/foods/{fid}", data={"name": "Rice", "unit": "kg",
                                                "confirm_merge": "1"})
        self.assertEqual(len(self.foods()), 1)
