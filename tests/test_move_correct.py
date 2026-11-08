import sqlite3

from tests.base import ApiTestCase


class MoveAndCorrectTests(ApiTestCase):
    def move(self, pid, group, quantity=None, unit=None):
        body = {"group": group}
        if quantity is not None:
            body["quantity"] = quantity
        if unit is not None:
            body["unit"] = unit
        return self.client.post(f"/api/purchases/{pid}/move", json=body)

    def edit(self, pid, **fields):
        return self.client.patch(f"/api/purchases/{pid}", json=fields)

    def delete(self, pid):
        return self.client.delete(f"/api/purchases/{pid}")

    def history(self):
        return self.client.get("/api/removals").get_json()

    def rows(self):
        return [(p["group"], p["quantity"], p["expiry"]) for p in self.list_purchases()]

    # The warned milestone has no API yet (the daily routine owns it), so these
    # tests seed and read it straight from the temporary database.
    def warn(self, pid, milestone):
        conn = sqlite3.connect(self.db_path)
        with conn:
            conn.execute("UPDATE purchase SET last_warned_milestone = ? WHERE id = ?",
                         (milestone, pid))
        conn.close()

    def warned(self, pid):
        conn = sqlite3.connect(self.db_path)
        value = conn.execute("SELECT last_warned_milestone FROM purchase WHERE id = ?",
                             (pid,)).fetchone()[0]
        conn.close()
        return value

    # moves
    def test_move_whole_purchase_changes_group(self):
        pid = self.buy("Rice", "2", "kg", "2027-01-01", "Pantry").get_json()["id"]
        self.assertEqual(self.move(pid, "Reserve").status_code, 200)
        self.assertEqual(self.rows(), [("Reserve", "2", "2027-01-01")])

    def test_move_part_splits_with_same_expiry(self):
        pid = self.buy("Rice", "2", "kg", "2027-01-01", "Pantry").get_json()["id"]
        self.assertEqual(self.move(pid, "Reserve", "500", "g").status_code, 200)
        self.assertCountEqual(self.rows(), [("Pantry", "1.5", "2027-01-01"),
                                            ("Reserve", "0.5", "2027-01-01")])
        self.assertEqual(self.history(), [])

    def test_move_more_than_available_rejected(self):
        pid = self.buy("Rice", "2", "kg", "2027-01-01").get_json()["id"]
        self.assertEqual(self.move(pid, "Reserve", "3", "kg").status_code, 400)
        self.assertEqual(self.rows(), [("Pantry", "2", "2027-01-01")])

    def test_move_whole_by_exact_quantity_keeps_one_purchase(self):
        pid = self.buy("Rice", "2", "kg").get_json()["id"]
        self.assertEqual(self.move(pid, "Reserve", "2000", "g").status_code, 200)
        self.assertEqual(self.rows(), [("Reserve", "2", None)])

    def test_move_to_same_group_or_invalid_group_or_unknown_purchase_rejected(self):
        pid = self.buy("Rice").get_json()["id"]
        self.assertEqual(self.move(pid, "Pantry").status_code, 400)
        self.assertEqual(self.move(pid, "Attic").status_code, 400)
        self.assertEqual(self.move(999, "Reserve").status_code, 404)

    def test_move_other_family_rejected(self):
        pid = self.buy("Rice", "2", "kg").get_json()["id"]
        self.assertEqual(self.move(pid, "Reserve", "1", "L").status_code, 400)

    def test_group_move_clears_warned_milestone(self):
        pid = self.buy("Rice", "2", "kg", "2027-01-01").get_json()["id"]
        self.warn(pid, 7)
        self.move(pid, "Reserve")
        self.assertIsNone(self.warned(pid))

    def test_partial_move_new_purchase_unwarned_original_untouched(self):
        pid = self.buy("Rice", "2", "kg", "2027-01-01").get_json()["id"]
        self.warn(pid, 7)
        self.move(pid, "Reserve", "1", "kg")
        self.assertEqual(self.warned(pid), 7)
        new_id = max(p["id"] for p in self.list_purchases())
        self.assertNotEqual(new_id, pid)
        self.assertIsNone(self.warned(new_id))

    # edits
    def test_edit_quantity_expiry_updates_list_and_totals(self):
        pid = self.buy("Rice", "2", "kg", "2027-01-01").get_json()["id"]
        r = self.edit(pid, quantity="3", expiry="2027-06")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.rows(), [("Pantry", "3", "2027-06-30")])
        self.assertEqual(self.client.get("/api/totals").get_json()[0]["total"], "3")
        self.assertEqual(self.list_purchases()[0]["expiry_display"], "2027-06")

    def test_edit_unit_same_family_converts_quantity(self):
        pid = self.buy("Rice", "2", "kg").get_json()["id"]
        self.assertEqual(self.edit(pid, quantity="500", unit="g").status_code, 200)
        self.assertEqual(self.rows(), [("Pantry", "0.5", None)])
        self.assertEqual(self.edit(pid, quantity="1", unit="L").status_code, 400)

    def test_edit_unit_alone_is_rejected_with_clear_message(self):
        pid = self.buy("Rice", "2", "kg").get_json()["id"]
        r = self.edit(pid, unit="g")
        self.assertEqual(r.status_code, 400)
        self.assertIn("quantity", r.get_json()["error"])
        self.assertEqual(self.rows(), [("Pantry", "2", None)])

    def test_edit_can_clear_expiry_and_change_group(self):
        pid = self.buy("Rice", "2", "kg", "2027-01-01").get_json()["id"]
        self.edit(pid, expiry="", group="Reserve")
        self.assertEqual(self.rows(), [("Reserve", "2", None)])

    def test_edit_invalid_rejected_without_change(self):
        pid = self.buy("Rice", "2", "kg", "2027-01-01").get_json()["id"]
        self.assertEqual(self.edit(pid, quantity="0").status_code, 400)
        self.assertEqual(self.edit(pid, expiry="soon").status_code, 400)
        self.assertEqual(self.edit(pid, group="Attic").status_code, 400)
        self.assertEqual(self.edit(999, quantity="1").status_code, 404)
        self.assertEqual(self.rows(), [("Pantry", "2", "2027-01-01")])

    def test_edit_creates_no_history(self):
        pid = self.buy("Rice", "2", "kg").get_json()["id"]
        self.edit(pid, quantity="1")
        self.assertEqual(self.history(), [])

    def test_expiry_change_clears_warned_milestone_but_quantity_edit_does_not(self):
        pid = self.buy("Rice", "2", "kg", "2027-01-01").get_json()["id"]
        self.warn(pid, 7)
        self.edit(pid, quantity="1", expiry="2027-01-01")
        self.assertEqual(self.warned(pid), 7)
        self.edit(pid, expiry="2027-02-01")
        self.assertIsNone(self.warned(pid))

    def test_edit_group_change_clears_warned_milestone(self):
        pid = self.buy("Rice", "2", "kg", "2027-01-01").get_json()["id"]
        self.warn(pid, 7)
        self.edit(pid, group="Reserve")
        self.assertIsNone(self.warned(pid))

    # delete
    def test_delete_removes_from_list_and_totals_without_history(self):
        keep = self.buy("Rice", "1", "kg").get_json()["id"]
        pid = self.buy("Rice", "2", "kg", "2027-01-01").get_json()["id"]
        self.assertEqual(self.delete(pid).status_code, 200)
        self.assertEqual([p["id"] for p in self.list_purchases()], [keep])
        self.assertEqual(self.client.get("/api/totals").get_json()[0]["total"], "1")
        self.assertEqual(self.history(), [])
        self.assertEqual(self.delete(pid).status_code, 404)

    def test_earlier_removals_survive_deleting_purchase(self):
        pid = self.buy("Rice", "2", "kg").get_json()["id"]
        self.client.post("/api/removals", json={
            "name": "Rice", "quantity": "1", "unit": "kg", "reason": "used"})
        self.delete(pid)
        self.assertEqual(len(self.history()), 1)

    # pages
    def test_pages_move_edit_delete(self):
        pid = self.buy("Rice", "2", "kg", "2027-01-01").get_json()["id"]
        self.assertEqual(self.client.get(f"/purchases/{pid}/edit").status_code, 200)
        r = self.client.post(f"/purchases/{pid}/edit",
                             data={"quantity": "3", "unit": "kg", "expiry": "2027-02-01",
                                   "group": "Pantry"})
        self.assertEqual(r.status_code, 302)
        r = self.client.post(f"/purchases/{pid}/move", data={"group": "Reserve"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.rows(), [("Reserve", "3", "2027-02-01")])
        bad = self.client.post(f"/purchases/{pid}/edit", data={"quantity": "x", "unit": "kg"})
        self.assertEqual(bad.status_code, 400)
        r = self.client.post(f"/purchases/{pid}/delete")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.list_purchases(), [])
