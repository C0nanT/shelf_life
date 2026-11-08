"""Expiry warnings: decide which purchases enter the digest and build its text.

Pure logic, no network and no clock: the caller supplies the date.
"""
from dataclasses import dataclass
from datetime import date

DEFAULT_MILESTONES = {"Pantry": (7, 0), "Reserve": (30, 7, 0)}


@dataclass
class Candidate:
    purchase_id: int
    name: str
    group: str
    expiry: date
    last_warned: int | None
    food_milestones: tuple | None = None


@dataclass
class Warning:
    purchase_id: int
    name: str
    group: str
    expiry: date
    days_left: int
    milestone: int


def parse_milestones(value):
    """Parse milestones from '30,7,0' or a list: a tuple, largest first.

    Blank means none (None). Raises ValueError with a user-safe message.
    """
    if isinstance(value, (list, tuple)):
        value = ",".join(str(v) for v in value)
    try:
        numbers = {int(p) for p in (value or "").split(",") if p.strip()}
    except ValueError:
        raise ValueError("Milestones must be whole numbers like 30,7,0") from None
    if any(n < 0 for n in numbers):
        raise ValueError("Milestones cannot be negative")
    return tuple(sorted(numbers, reverse=True)) or None


def current_milestone(days_left, milestones):
    """Smallest milestone >= days_left; expired purchases use 0."""
    if days_left < 0:
        return 0
    eligible = [m for m in milestones if m >= days_left]
    return min(eligible) if eligible else None


def due_warnings(candidates, today):
    """Candidates reaching a milestone different from the last warned one."""
    due = []
    for c in candidates:
        milestones = c.food_milestones or DEFAULT_MILESTONES[c.group]
        days_left = (c.expiry - today).days
        milestone = current_milestone(days_left, milestones)
        if milestone is not None and milestone != c.last_warned:
            due.append(Warning(c.purchase_id, c.name, c.group, c.expiry,
                               days_left, milestone))
    return sorted(due, key=lambda w: (w.expiry, w.purchase_id))


def describe_days(days_left):
    if days_left < 0:
        n = -days_left
        return f"expired {n} day{'s' if n != 1 else ''} ago"
    if days_left == 0:
        return "expires today"
    return f"{days_left} day{'s' if days_left != 1 else ''} left"


def build_digest(warnings):
    lines = ["Stock: expiry warnings"]
    for w in warnings:
        lines.append(f"- {w.name} ({w.group}): {describe_days(w.days_left)}"
                     f" [{w.expiry.strftime("%d/%m/%Y")}]")
    return "\n".join(lines)


def load_candidates(conn):
    """Purchases with a balance and an expiry date."""
    rows = conn.execute(
        'SELECT p.id, f.name, p."group", p.expiry_date, p.last_warned_milestone,'
        " f.warning_milestones FROM purchase p JOIN food f ON f.id = p.food_id"
        " WHERE p.expiry_date IS NOT NULL AND CAST(p.quantity AS REAL) > 0"
    ).fetchall()
    return [Candidate(r["id"], r["name"], r["group"],
                      date.fromisoformat(r["expiry_date"]),
                      r["last_warned_milestone"],
                      parse_milestones(r["warning_milestones"])) for r in rows]
