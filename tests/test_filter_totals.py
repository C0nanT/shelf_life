from tests.base import ApiTestCase


class FilterAndSearchTests(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.buy("Rice", "1", "kg", "2027-03-01", "Reserve")
        self.buy("Beans", "1", "kg", "2027-01-01", "Pantry")
        self.buy("Rice", "2", "kg", "2027-02-01", "Pantry")

    def names(self, query):
        response = self.client.get("/api/purchases" + query)
        self.assertEqual(response.status_code, 200)
        return [(p["name"], p["group"], p["expiry"]) for p in response.get_json()]

    def test_group_filter_keeps_expiry_order(self):
        self.assertEqual(self.names("?group=Pantry"), [
            ("Beans", "Pantry", "2027-01-01"), ("Rice", "Pantry", "2027-02-01")])
        self.assertEqual(self.names("?group=Reserve"),
                         [("Rice", "Reserve", "2027-03-01")])

    def test_search_is_case_insensitive_substring(self):
        self.assertEqual([n for n, _, _ in self.names("?q=RIC")], ["Rice", "Rice"])
        self.assertEqual(self.names("?q=zzz"), [])

    def test_filter_and_search_combine(self):
        self.assertEqual(self.names("?group=Pantry&q=rice"),
                         [("Rice", "Pantry", "2027-02-01")])

    def test_invalid_group_rejected(self):
        self.assertEqual(self.client.get("/api/purchases?group=Garage").status_code, 400)

    def test_index_page_applies_filter(self):
        html = self.client.get("/?group=Reserve&q=rice").get_data(as_text=True)
        self.assertIn("01/03/2027", html)
        self.assertNotIn("Beans", html)


class TotalsTests(ApiTestCase):
    def totals(self):
        response = self.client.get("/api/totals")
        self.assertEqual(response.status_code, 200)
        return response.get_json()

    def test_totals_per_food_with_group_split(self):
        self.buy("Rice", "1", "kg", "", "Pantry")
        self.buy("Rice", "2", "kg", "", "Reserve")
        self.buy("Rice", "0.5", "kg", "", "Reserve")
        self.buy("Eggs", "6", "unit", "", "Pantry")
        self.assertEqual(self.totals(), [
            {"name": "Eggs", "unit": "unit", "total": "6",
             "by_group": {"Pantry": "6", "Reserve": "0"}},
            {"name": "Rice", "unit": "kg", "total": "3.5",
             "by_group": {"Pantry": "1", "Reserve": "2.5"}},
        ])

    def test_same_family_units_add_exactly(self):
        self.buy("Flour", "1", "kg")
        self.buy("Flour", "500", "g")
        self.buy("Flour", "0.1", "kg")
        self.buy("Flour", "0.2", "kg")
        [flour] = self.totals()
        self.assertEqual((flour["total"], flour["unit"]), ("1.8", "kg"))

    def test_totals_page_renders(self):
        self.buy("Rice", "1", "kg")
        html = self.client.get("/totals").get_data(as_text=True)
        self.assertIn("Rice", html)
        self.assertIn("1 kg", html)
