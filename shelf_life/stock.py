"""Stock rules: foods and purchases. Independent of the web layer."""
import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from . import units, warnings

GROUPS = ("Pantry", "Reserve")
REASONS = ("used", "discarded")


class StockError(ValueError):
    """A business rule was violated; the message is safe to show the user."""


class NotFound(StockError):
    """The requested purchase does not exist."""


class NeedsConfirmation(StockError):
    """The action would merge two foods and must be confirmed first."""


def check_group(group):
    if group not in GROUPS:
        raise StockError("Group must be Pantry or Reserve")


def normalize_name(name):
    return " ".join(name.split()).casefold()


def parse_expiry(text):
    """Return (date, precision) from 'YYYY-MM-DD', 'YYYY-MM', or blank."""
    text = (text or "").strip()
    if not text:
        return None, None
    pieces = text.split("-")
    try:
        if len(pieces[0]) == 4:
            numbers = [int(p) for p in pieces]
            if len(numbers) == 3:
                return date(*numbers), "day"
            if len(numbers) == 2:
                year, month = numbers
                return date(year, month, calendar.monthrange(year, month)[1]), "month"
    except (ValueError, calendar.IllegalMonthError):
        pass
    raise StockError("Expiry must be YYYY-MM-DD, YYYY-MM, or blank")


@dataclass
class PurchaseView:
    id: int
    food_id: int
    name: str
    quantity: Decimal
    unit: str
    expiry: date | None
    expiry_precision: str | None
    group: str
    expired: bool

    @property
    def expiry_display(self):
        if self.expiry is None:
            return None
        if self.expiry_precision == "month":
            return self.expiry.strftime("%Y-%m")
        return self.expiry.isoformat()


class Stock:
    def __init__(self, conn, clock):
        self.conn = conn
        self.clock = clock

    def record_purchase(self, name, quantity, unit, expiry, group):
        display_name = " ".join((name or "").split())
        if not display_name:
            raise StockError("Name is required")
        check_group(group)
        try:
            qty = units.parse_quantity(quantity)
            units.family(unit)
        except units.UnitError as e:
            raise StockError(str(e)) from None
        expiry_date, precision = parse_expiry(expiry)

        with self.conn:
            food = self.conn.execute(
                "SELECT id, unit FROM food WHERE normalized_name = ?",
                (normalize_name(display_name),),
            ).fetchone()
            if food is None:
                cur = self.conn.execute(
                    "INSERT INTO food (name, normalized_name, unit) VALUES (?, ?, ?)",
                    (display_name, normalize_name(display_name), unit),
                )
                food_id, food_unit = cur.lastrowid, unit
            else:
                food_id, food_unit = food["id"], food["unit"]
            try:
                qty = units.convert(qty, unit, food_unit)
            except units.UnitError:
                raise StockError(
                    f"{display_name} is tracked in {food_unit}; "
                    f"{unit} is a different unit family"
                ) from None
            return self._insert_purchase(
                food_id, qty, expiry_date.isoformat() if expiry_date else None,
                precision, group)

    def _insert_purchase(self, food_id, qty, expiry_iso, precision, group):
        cur = self.conn.execute(
            'INSERT INTO purchase (food_id, quantity, expiry_date, expiry_precision,'
            ' "group", recorded_date) VALUES (?, ?, ?, ?, ?, ?)',
            (food_id, units.format_quantity(qty), expiry_iso, precision,
             group, self.clock().isoformat()))
        return cur.lastrowid

    def suggest_foods(self, text):
        """Foods whose name contains the text (case-insensitive), with their unit."""
        needle = normalize_name(text or "")
        rows = self.conn.execute(
            "SELECT name, normalized_name, unit FROM food ORDER BY normalized_name"
        ).fetchall()
        return [{"name": r["name"], "unit": r["unit"]}
                for r in rows if needle in r["normalized_name"]]

    def list_purchases(self, group=None, search=None):
        """Purchases by nearest expiry (expired ones sort first); no expiry last.

        Optionally limited to one group and to names containing `search`
        (case-insensitive).
        """
        if group:
            check_group(group)
        needle = normalize_name(search or "")
        today = self.clock()
        sql = ('SELECT p.id, p.food_id, f.name, p.quantity, f.unit, p.expiry_date,'
               ' p.expiry_precision, p."group" FROM purchase p JOIN food f ON f.id = p.food_id'
               " WHERE CAST(p.quantity AS REAL) > 0")
        args = []
        if group:
            sql += ' AND p."group" = ?'
            args.append(group)
        if needle:
            sql += " AND instr(f.normalized_name, ?) > 0"
            args.append(needle)
        rows = self.conn.execute(
            sql + " ORDER BY p.expiry_date IS NULL, p.expiry_date, p.id", args).fetchall()
        result = []
        for r in rows:
            expiry = date.fromisoformat(r["expiry_date"]) if r["expiry_date"] else None
            result.append(PurchaseView(
                id=r["id"], food_id=r["food_id"], name=r["name"],
                quantity=Decimal(r["quantity"]), unit=r["unit"], expiry=expiry,
                expiry_precision=r["expiry_precision"], group=r["group"],
                expired=expiry is not None and expiry < today,
            ))
        return result

    def totals(self):
        """Total per food in the food's unit, with the split by group."""
        totals = {}
        for p in self.list_purchases():
            entry = totals.setdefault(p.food_id, {
                "name": p.name, "unit": p.unit, "total": Decimal(0),
                "by_group": {g: Decimal(0) for g in GROUPS},
            })
            entry["total"] += p.quantity
            entry["by_group"][p.group] += p.quantity
        return sorted(totals.values(), key=lambda e: normalize_name(e["name"]))

    def record_removal(self, name, quantity, unit, reason, purchase_id=None):
        """Deduct from a chosen purchase, or from the nearest expiry onwards.

        All-or-nothing: raises StockError and changes nothing if not enough is available.
        """
        if reason not in REASONS:
            raise StockError("Reason must be used or discarded")
        try:
            qty = units.parse_quantity(quantity)
            units.family(unit)
        except units.UnitError as e:
            raise StockError(str(e)) from None

        with self.conn:
            if purchase_id is not None:
                row = self.conn.execute(
                    "SELECT food_id FROM purchase WHERE id = ?", (purchase_id,)
                ).fetchone()
                if row is None:
                    raise StockError("Purchase not found")
                food = self.conn.execute(
                    "SELECT id, name, unit FROM food WHERE id = ?", (row["food_id"],)
                ).fetchone()
            else:
                food = self.conn.execute(
                    "SELECT id, name, unit FROM food WHERE normalized_name = ?",
                    (normalize_name(name or ""),),
                ).fetchone()
                if food is None:
                    raise StockError("Unknown food")
            try:
                qty = units.convert(qty, unit, food["unit"])
            except units.UnitError:
                raise StockError(
                    f"{food['name']} is tracked in {food['unit']}; "
                    f"{unit} is a different unit family"
                ) from None

            sql = ("SELECT id, quantity FROM purchase WHERE food_id = ?"
                   " AND CAST(quantity AS REAL) > 0")
            args = [food["id"]]
            if purchase_id is not None:
                sql += " AND id = ?"
                args.append(purchase_id)
            sql += " ORDER BY expiry_date IS NULL, expiry_date, recorded_date, id"
            candidates = self.conn.execute(sql, args).fetchall()
            if sum(Decimal(c["quantity"]) for c in candidates) < qty:
                raise StockError(f"Not enough {food['name']} available")

            today = self.clock().isoformat()
            left = qty
            for c in candidates:
                if left <= 0:
                    break
                have = Decimal(c["quantity"])
                take = min(left, have)
                left -= take
                self.conn.execute(
                    "UPDATE purchase SET quantity = ? WHERE id = ?",
                    (units.format_quantity(have - take), c["id"]),
                )
                self.conn.execute(
                    "INSERT INTO removal (removed_date, food_id, purchase_id, quantity, reason)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (today, food["id"], c["id"], units.format_quantity(take), reason),
                )

    def _purchase_row(self, purchase_id):
        row = self.conn.execute(
            'SELECT p.id, p.food_id, p.quantity, p.expiry_date, p.expiry_precision,'
            ' p."group", f.name, f.unit FROM purchase p JOIN food f ON f.id = p.food_id'
            " WHERE p.id = ? AND CAST(p.quantity AS REAL) > 0",
            (purchase_id,),
        ).fetchone()
        if row is None:
            raise NotFound("Purchase not found")
        return row

    def get_purchase(self, purchase_id):
        r = self._purchase_row(purchase_id)
        expiry = date.fromisoformat(r["expiry_date"]) if r["expiry_date"] else None
        return PurchaseView(
            id=r["id"], food_id=r["food_id"], name=r["name"],
            quantity=Decimal(r["quantity"]), unit=r["unit"], expiry=expiry,
            expiry_precision=r["expiry_precision"], group=r["group"],
            expired=expiry is not None and expiry < self.clock(),
        )

    def _quantity_in_food_unit(self, row, quantity, unit):
        try:
            qty = units.parse_quantity(quantity)
            return units.convert(qty, unit or row["unit"], row["unit"])
        except units.UnitError as e:
            raise StockError(str(e)) from None

    def move_purchase(self, purchase_id, group, quantity=None, unit=None):
        """Move a whole purchase, or part of it, to another group.

        Not a removal: no history line. Moving the whole purchase clears its
        warned milestone; moving part leaves the original alone and creates an
        unwarned purchase with the same expiry.
        """
        check_group(group)
        with self.conn:
            row = self._purchase_row(purchase_id)
            if row["group"] == group:
                raise StockError(f"Purchase is already in {group}")
            have = Decimal(row["quantity"])
            if quantity in (None, ""):
                qty = have
            else:
                qty = self._quantity_in_food_unit(row, quantity, unit)
            if qty > have:
                raise StockError(f"Not enough {row['name']} in this purchase")
            if qty == have:
                self.conn.execute(
                    'UPDATE purchase SET "group" = ?, last_warned_milestone = NULL'
                    " WHERE id = ?", (group, purchase_id))
                return purchase_id
            self.conn.execute("UPDATE purchase SET quantity = ? WHERE id = ?",
                              (units.format_quantity(have - qty), purchase_id))
            return self._insert_purchase(row["food_id"], qty, row["expiry_date"],
                                         row["expiry_precision"], group)

    def edit_purchase(self, purchase_id, **fields):
        """Correct quantity, unit (same family), expiry, or group; no removal is recorded.

        Only the keys given are changed. A changed expiry or group clears the
        warned milestone.
        """
        if set(fields) - {"quantity", "unit", "expiry", "group"}:
            raise StockError("Unknown field")
        with self.conn:
            row = self._purchase_row(purchase_id)
            qty = Decimal(row["quantity"])
            if fields.get("quantity") not in (None, ""):
                qty = self._quantity_in_food_unit(row, fields["quantity"], fields.get("unit"))
            elif fields.get("unit"):
                raise StockError("Changing the unit needs a quantity in the new unit")
            expiry_date, precision = row["expiry_date"], row["expiry_precision"]
            if "expiry" in fields:
                parsed, precision = parse_expiry(fields["expiry"])
                expiry_date = parsed.isoformat() if parsed else None
            group = fields.get("group") or row["group"]
            check_group(group)
            changed = expiry_date != row["expiry_date"] or group != row["group"]
            self.conn.execute(
                'UPDATE purchase SET quantity = ?, expiry_date = ?, expiry_precision = ?,'
                ' "group" = ?' + (", last_warned_milestone = NULL" if changed else "") +
                " WHERE id = ?",
                (units.format_quantity(qty), expiry_date, precision, group, purchase_id))

    def delete_purchase(self, purchase_id):
        """Delete a purchase recorded by mistake. History lines are kept."""
        with self.conn:
            self._purchase_row(purchase_id)
            self.conn.execute("DELETE FROM purchase WHERE id = ?", (purchase_id,))

    def list_removals(self):
        rows = self.conn.execute(
            "SELECT r.removed_date, f.name, f.unit, r.quantity, r.reason"
            " FROM removal r JOIN food f ON f.id = r.food_id ORDER BY r.id DESC"
        ).fetchall()
        return [{"date": r["removed_date"], "food": r["name"],
                 "quantity": r["quantity"], "unit": r["unit"], "reason": r["reason"]}
                for r in rows]

    # foods
    def list_foods(self):
        rows = self.conn.execute(
            "SELECT f.id, f.name, f.unit, f.warning_milestones,"
            " COALESCE(c.n, 0) AS purchase_count FROM food f"
            " LEFT JOIN (SELECT food_id, COUNT(*) AS n FROM purchase GROUP BY food_id) c"
            " ON c.food_id = f.id ORDER BY f.normalized_name"
        ).fetchall()
        return [{"id": r["id"], "name": r["name"], "unit": r["unit"],
                 "milestones": r["warning_milestones"] or "",
                 "purchase_count": r["purchase_count"]} for r in rows]

    def update_food(self, food_id, name=None, unit=None, milestones=None,
                    confirm_merge=False):
        """Rename, change unit, or set exception milestones (any key may be omitted).

        Renaming to another food's name needs `confirm_merge`; the food is then
        merged into the destination, whose milestones win.
        """
        with self.conn:
            food = self.conn.execute(
                "SELECT * FROM food WHERE id = ?", (food_id,)).fetchone()
            if food is None:
                raise NotFound("Food not found")
            display = " ".join(name.split()) if name is not None else food["name"]
            if not display:
                raise StockError("Name is required")
            unit = unit or food["unit"]
            try:
                units.family(unit)
            except units.UnitError as e:
                raise StockError(str(e)) from None
            target = self.conn.execute(
                "SELECT * FROM food WHERE normalized_name = ? AND id != ?",
                (normalize_name(display), food_id)).fetchone()
            if target is not None:
                return self._merge_foods(food, target, confirm_merge)
            if unit != food["unit"]:
                self._change_unit(food, unit)
            new_milestones = food["warning_milestones"]
            if milestones is not None:
                new_milestones = self._parse_milestones(milestones)
            self.conn.execute(
                "UPDATE food SET name = ?, normalized_name = ?, unit = ?,"
                " warning_milestones = ? WHERE id = ?",
                (display, normalize_name(display), unit, new_milestones, food_id))
            if new_milestones != food["warning_milestones"]:
                self.conn.execute(
                    "UPDATE purchase SET last_warned_milestone = NULL WHERE food_id = ?",
                    (food_id,))

    @staticmethod
    def _parse_milestones(value):
        try:
            parsed = warnings.parse_milestones(value)
        except ValueError as e:
            raise StockError(str(e)) from None
        return ",".join(str(n) for n in parsed) if parsed else None

    def _rescale(self, food_id, from_unit, to_unit):
        """Re-express a food's stored quantities in another unit of the same family."""
        for table in ("purchase", "removal"):
            rows = self.conn.execute(
                f"SELECT id, quantity FROM {table} WHERE food_id = ?",
                (food_id,)).fetchall()
            self.conn.executemany(
                f"UPDATE {table} SET quantity = ? WHERE id = ?",
                [(units.format_quantity(
                    units.convert(Decimal(r["quantity"]), from_unit, to_unit)), r["id"])
                  for r in rows])

    def _change_unit(self, food, unit):
        if units.family(unit) != units.family(food["unit"]):
            used = self.conn.execute(
                "SELECT (SELECT COUNT(*) FROM purchase WHERE food_id = ?)"
                " + (SELECT COUNT(*) FROM removal WHERE food_id = ?)",
                (food["id"], food["id"])).fetchone()[0]
            if used:
                raise StockError(
                    f"{food['name']} has recorded purchases; "
                    "its unit family cannot change")
            return
        self._rescale(food["id"], food["unit"], unit)

    def _merge_foods(self, source, target, confirm_merge):
        if units.family(source["unit"]) != units.family(target["unit"]):
            raise StockError(
                f"Cannot merge {source['name']} ({source['unit']}) into "
                f"{target['name']} ({target['unit']}): different unit families")
        if not confirm_merge:
            raise NeedsConfirmation(
                f"{target['name']} already exists. Merge {source['name']} into it?")
        self._rescale(source["id"], source["unit"], target["unit"])
        self.conn.execute(
            "UPDATE purchase SET food_id = ?, last_warned_milestone = NULL"
            " WHERE food_id = ?", (target["id"], source["id"]))
        self.conn.execute("UPDATE removal SET food_id = ? WHERE food_id = ?",
                          (target["id"], source["id"]))
        self.conn.execute("DELETE FROM food WHERE id = ?", (source["id"],))
