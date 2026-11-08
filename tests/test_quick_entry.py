from tests.base import ApiTestCase


class FoodSuggestionTests(ApiTestCase):
    def suggest(self, q):
        return self.client.get("/api/foods", query_string={"q": q}).get_json()

    def test_partial_name_suggests_matching_foods_with_their_unit(self):
        self.buy("Rice", "1", "kg")
        self.buy("Rice", "2", "kg")
        self.buy("Ricotta", "300", "g")
        self.buy("Milk", "1", "L")
        self.assertEqual(self.suggest("ric"),
                         [{"name": "Rice", "unit": "kg"}, {"name": "Ricotta", "unit": "g"}])

    def test_match_is_case_insensitive_and_ignores_surrounding_space(self):
        self.buy("Rice", "1", "kg")
        self.assertEqual(self.suggest("  RIC "), [{"name": "Rice", "unit": "kg"}])

    def test_no_match_gives_empty_list(self):
        self.buy("Rice", "1", "kg")
        self.assertEqual(self.suggest("zzz"), [])


class SaveAndAddAnotherTests(ApiTestCase):
    def post(self, **extra):
        data = {"name": "Rice", "quantity": "1", "unit": "kg", "group": "Reserve"}
        data.update(extra)
        return self.client.post("/purchases", data=data)

    def test_save_and_add_another_records_and_returns_to_empty_form(self):
        response = self.post(again="1")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/purchases/new", response.headers["Location"])
        self.assertEqual(len(self.list_purchases()), 1)
        page = self.client.get(response.headers["Location"]).get_data(as_text=True)
        self.assertIn("Rice", page)  # confirmation of what was saved

    def test_plain_save_still_goes_to_list(self):
        response = self.post()
        self.assertTrue(response.headers["Location"].endswith("/"))

    def test_only_name_quantity_unit_group_required(self):
        response = self.post(again="1", expiry="")
        self.assertEqual(response.status_code, 302)

    def test_error_on_save_and_add_another_keeps_form(self):
        response = self.post(again="1", quantity="abc")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.list_purchases(), [])
