"""Stock rules: foods and purchases. Independent of the web layer."""
import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from . import units

GROUPS = ("Pantry", "Reserve")


class StockError(ValueError):
    """A business rule was violated; the message is safe to show the user."""


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
        if group not in GROUPS:
            raise StockError("Group must be Pantry or Reserve")
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
            cur = self.conn.execute(
                'INSERT INTO purchase (food_id, quantity, expiry_date, expiry_precision,'
                ' "group", recorded_date) VALUES (?, ?, ?, ?, ?, ?)',
                (food_id, units.format_quantity(qty),
                 expiry_date.isoformat() if expiry_date else None, precision,
                 group, self.clock().isoformat()),
            )
            return cur.lastrowid

    def suggest_foods(self, text):
        """Foods whose name contains the text (case-insensitive), with their unit."""
        needle = normalize_name(text or "")
        rows = self.conn.execute(
            "SELECT name, normalized_name, unit FROM food ORDER BY normalized_name"
        ).fetchall()
        return [{"name": r["name"], "unit": r["unit"]}
                for r in rows if needle in r["normalized_name"]]

    def list_purchases(self):
        """Purchases by nearest expiry (expired ones sort first); no expiry last."""
        today = self.clock()
        rows = self.conn.execute(
            'SELECT p.id, p.food_id, f.name, p.quantity, f.unit, p.expiry_date,'
            ' p.expiry_precision, p."group" FROM purchase p JOIN food f ON f.id = p.food_id'
            " ORDER BY p.expiry_date IS NULL, p.expiry_date, p.id"
        ).fetchall()
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
