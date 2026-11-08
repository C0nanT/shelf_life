from tests.base import ApiTestCase


class RecordPurchaseTests(ApiTestCase):
    def test_recorded_purchase_appears_in_list(self):
        response = self.buy("Rice", "2.5", "kg", "2027-01-15", "Reserve")
        self.assertEqual(response.status_code, 201)
        [item] = self.list_purchases()
        self.assertEqual(item["name"], "Rice")
        self.assertEqual(item["quantity"], "2.5")
        self.assertEqual(item["unit"], "kg")
        self.assertEqual(item["expiry"], "2027-01-15")
        self.assertEqual(item["expiry_display"], "2027-01-15")
        self.assertEqual(item["group"], "Reserve")
        self.assertFalse(item["expired"])

    def test_decimal_quantities_are_exact(self):
        self.buy("Flour", "0.1", "kg")
        self.buy("Flour", "0.2", "kg")
        quantities = sorted(p["quantity"] for p in self.list_purchases())
        self.assertEqual(quantities, ["0.1", "0.2"])

    def test_all_units_accepted(self):
        for unit, name in [("unit", "Eggs"), ("g", "Salt"), ("kg", "Rice"),
                           ("ml", "Vinegar"), ("L", "Milk")]:
            self.assertEqual(self.buy(name, "1", unit).status_code, 201, unit)

    def test_unknown_unit_rejected(self):
        self.assertEqual(self.buy("Rice", "1", "lb").status_code, 400)

    def test_invalid_quantity_rejected(self):
        for bad in ["0", "-1", "abc", ""]:
            self.assertEqual(self.buy("Rice", bad).status_code, 400, bad)

    def test_invalid_group_rejected(self):
        self.assertEqual(self.buy(group="Garage").status_code, 400)

    def test_blank_name_rejected(self):
        self.assertEqual(self.buy("   ").status_code, 400)

    def test_month_and_year_expiry_valid_through_last_day_and_shown_as_month(self):
        self.today = self.today.replace(year=2027, month=2, day=28)
        self.buy("Pasta", "1", "kg", "2027-02")
        [item] = self.list_purchases()
        self.assertEqual(item["expiry_display"], "2027-02")
        self.assertFalse(item["expired"])
        self.today = self.today.replace(month=3, day=1)
        [item] = self.list_purchases()
        self.assertTrue(item["expired"])

    def test_invalid_expiry_rejected(self):
        for bad in ["2027-13", "2027-02-30", "soon", "2027"]:
            self.assertEqual(self.buy(expiry=bad).status_code, 400, bad)

    def test_blank_expiry_allowed(self):
        self.assertEqual(self.buy("Salt", "1", "kg", "").status_code, 201)
        [item] = self.list_purchases()
        self.assertIsNone(item["expiry"])
        self.assertIsNone(item["expiry_display"])
        self.assertFalse(item["expired"])


class FoodIdentityTests(ApiTestCase):
    def test_same_name_different_case_is_one_food(self):
        self.buy("Rice", "1", "kg")
        self.buy("  rice ", "500", "g")
        items = self.list_purchases()
        self.assertEqual(len(items), 2)
        self.assertEqual({i["food_id"] for i in items}, {items[0]["food_id"]})
        self.assertEqual({i["name"] for i in items}, {"Rice"})

    def test_first_purchase_sets_food_unit_and_later_same_family_is_converted(self):
        self.buy("Rice", "1", "kg")
        self.buy("Rice", "500", "g")
        quantities = sorted(p["quantity"] for p in self.list_purchases())
        self.assertEqual(quantities, ["0.5", "1"])
        self.assertEqual({p["unit"] for p in self.list_purchases()}, {"kg"})

    def test_different_unit_family_rejected(self):
        self.buy("Rice", "1", "kg")
        self.assertEqual(self.buy("rice", "1", "L").status_code, 400)
        self.assertEqual(self.buy("RICE", "1", "unit").status_code, 400)
        self.assertEqual(len(self.list_purchases()), 1)

    def test_each_purchase_is_its_own_record(self):
        self.buy("Rice", "1", "kg", "2027-01-01", "Pantry")
        self.buy("Rice", "2", "kg", "2027-06-01", "Reserve")
        items = self.list_purchases()
        self.assertEqual(len({i["id"] for i in items}), 2)
        self.assertEqual([(i["quantity"], i["group"]) for i in items],
                         [("1", "Pantry"), ("2", "Reserve")])


class ListOrderTests(ApiTestCase):
    def test_expired_first_then_nearest_expiry_then_no_expiry_last(self):
        self.buy("NoExpiry", expiry="")
        self.buy("Later", expiry="2027-05-01")
        self.buy("Soon", expiry="2026-12-01")
        self.buy("Expired", expiry="2026-11-01")
        self.buy("LongExpired", expiry="2026-01-01")
        items = self.list_purchases()
        self.assertEqual([i["name"] for i in items],
                         ["LongExpired", "Expired", "Soon", "Later", "NoExpiry"])
        self.assertEqual([i["expired"] for i in items],
                         [True, True, False, False, False])

    def test_expiring_today_is_not_expired(self):
        self.buy("Today", expiry="2026-11-08")
        [item] = self.list_purchases()
        self.assertFalse(item["expired"])

    def test_ties_resolved_by_recording_order(self):
        self.buy("First", expiry="2027-01-01")
        self.buy("Second", expiry="2027-01-01")
        self.assertEqual([i["name"] for i in self.list_purchases()], ["First", "Second"])


class PageTests(ApiTestCase):
    def test_form_post_records_purchase_and_page_lists_it_highlighted_when_expired(self):
        response = self.client.post("/purchases", data={
            "name": "Milk", "quantity": "1", "unit": "L",
            "expiry": "2026-11-01", "group": "Pantry"})
        self.assertEqual(response.status_code, 302)
        page = self.client.get("/").get_data(as_text=True)
        self.assertIn("Milk", page)
        self.assertIn("expired", page)

    def test_form_page_renders(self):
        self.assertEqual(self.client.get("/purchases/new").status_code, 200)

    def test_form_error_shows_message(self):
        response = self.client.post("/purchases", data={
            "name": "", "quantity": "1", "unit": "kg", "expiry": "", "group": "Pantry"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Name is required", response.get_data(as_text=True))
