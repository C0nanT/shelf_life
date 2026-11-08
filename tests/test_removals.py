from tests.base import ApiTestCase


class RemovalTests(ApiTestCase):
    def remove(self, name="Rice", quantity="1", unit="kg", reason="used", purchase_id=None):
        body = {"name": name, "quantity": quantity, "unit": unit, "reason": reason}
        if purchase_id is not None:
            body["purchase_id"] = purchase_id
        return self.client.post("/api/removals", json=body)

    def history(self):
        return self.client.get("/api/removals").get_json()

    def quantities(self):
        return [(p["expiry"], p["quantity"]) for p in self.list_purchases()]

    def test_deducts_from_nearest_expiry_and_continues_into_next(self):
        self.buy("Rice", "1", "kg", "2027-03-01")
        self.buy("Rice", "2", "kg", "2027-01-01")
        self.buy("Rice", "5", "kg", "")
        self.assertEqual(self.remove(quantity="2.5").status_code, 201)
        self.assertEqual(self.quantities(),
                         [("2027-03-01", "0.5"), (None, "5")])

    def test_no_expiry_comes_last(self):
        self.buy("Rice", "1", "kg", "")
        self.buy("Rice", "1", "kg", "2027-05-01")
        self.remove(quantity="1")
        self.assertEqual(self.quantities(), [(None, "1")])

    def test_ties_deduct_earliest_recorded_first(self):
        first = self.buy("Rice", "1", "kg", "2027-01-01").get_json()["id"]
        self.buy("Rice", "1", "kg", "2027-01-01")
        self.remove(quantity="1")
        remaining = self.list_purchases()
        self.assertEqual(len(remaining), 1)
        self.assertNotEqual(remaining[0]["id"], first)

    def test_can_choose_purchase(self):
        self.buy("Rice", "1", "kg", "2027-01-01")
        later = self.buy("Rice", "2", "kg", "2027-06-01").get_json()["id"]
        self.assertEqual(self.remove(quantity="500", unit="g", purchase_id=later).status_code, 201)
        self.assertEqual(self.quantities(), [("2027-01-01", "1"), ("2027-06-01", "1.5")])

    def test_chosen_purchase_too_small_rejected_without_change(self):
        self.buy("Rice", "1", "kg", "2027-01-01")
        small = self.buy("Rice", "1", "kg", "2027-06-01").get_json()["id"]
        self.assertEqual(self.remove(quantity="1.5", purchase_id=small).status_code, 400)
        self.assertEqual(self.quantities(), [("2027-01-01", "1"), ("2027-06-01", "1")])
        self.assertEqual(self.history(), [])

    def test_unit_conversion_within_family_with_decimals(self):
        self.buy("Milk", "2", "L")
        self.assertEqual(self.remove("Milk", "250.5", "ml").status_code, 201)
        self.assertEqual(self.quantities(), [(None, "1.7495")])

    def test_other_family_rejected(self):
        self.buy("Rice", "1", "kg")
        self.assertEqual(self.remove("Rice", "1", "L").status_code, 400)

    def test_too_large_rejected_entirely(self):
        self.buy("Rice", "1", "kg", "2027-01-01")
        self.buy("Rice", "1", "kg", "2027-02-01")
        self.assertEqual(self.remove(quantity="2.001").status_code, 400)
        self.assertEqual(self.quantities(), [("2027-01-01", "1"), ("2027-02-01", "1")])
        self.assertEqual(self.history(), [])

    def test_unknown_food_invalid_quantity_and_reason_rejected(self):
        self.buy("Rice", "1", "kg")
        self.assertEqual(self.remove("Beans").status_code, 400)
        self.assertEqual(self.remove(quantity="0").status_code, 400)
        self.assertEqual(self.remove(reason="stolen").status_code, 400)

    def test_name_is_case_insensitive(self):
        self.buy("Rice", "1", "kg")
        self.assertEqual(self.remove("rice", "1").status_code, 201)

    def test_emptied_purchase_leaves_list_but_stays_in_history(self):
        self.buy("Rice", "1", "kg")
        self.remove(quantity="1", reason="discarded")
        self.assertEqual(self.list_purchases(), [])
        [line] = self.history()
        self.assertEqual(line["food"], "Rice")
        self.assertEqual(line["quantity"], "1")
        self.assertEqual(line["unit"], "kg")
        self.assertEqual(line["reason"], "discarded")
        self.assertEqual(line["date"], "2026-11-08")

    def test_removal_spanning_purchases_makes_one_line_each(self):
        self.buy("Rice", "1", "kg", "2027-01-01")
        self.buy("Rice", "1", "kg", "2027-02-01")
        self.remove(quantity="1500", unit="g")
        self.assertEqual(sorted(h["quantity"] for h in self.history()), ["0.5", "1"])

    def test_history_page_renders(self):
        self.buy("Rice", "1", "kg")
        self.remove(quantity="1")
        html = self.client.get("/history").get_data(as_text=True)
        self.assertIn("Rice", html)
        self.assertIn("used", html)
