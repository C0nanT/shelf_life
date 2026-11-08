"""Unit families and exact decimal conversion."""
from decimal import Decimal, InvalidOperation

# unit -> (family, factor to the family's base unit)
UNITS = {
    "unit": ("unit", Decimal(1)),
    "g": ("weight", Decimal(1)),
    "kg": ("weight", Decimal(1000)),
    "ml": ("volume", Decimal(1)),
    "L": ("volume", Decimal(1000)),
}


class UnitError(ValueError):
    pass


def family(unit):
    if unit not in UNITS:
        raise UnitError(f"Unknown unit: {unit!r}")
    return UNITS[unit][0]


def convert(quantity, from_unit, to_unit):
    """Convert within a family; raises UnitError across families."""
    if family(from_unit) != family(to_unit):
        raise UnitError(f"Cannot convert {from_unit} to {to_unit}")
    return quantity * UNITS[from_unit][1] / UNITS[to_unit][1]


def parse_quantity(text):
    """Parse a positive, finite decimal quantity."""
    try:
        value = Decimal(str(text).strip())
    except InvalidOperation:
        raise UnitError("Quantity must be a number") from None
    if not value.is_finite() or value <= 0:
        raise UnitError("Quantity must be greater than zero")
    return value


def format_quantity(value):
    """Plain decimal text without exponent or trailing zeros."""
    if value == value.to_integral_value():
        return str(int(value))
    return format(value.normalize(), "f")
