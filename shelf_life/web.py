"""Web layer: translates requests into Stock calls."""
from flask import Blueprint, current_app, g, jsonify, redirect, render_template, request, url_for

from . import db, units
from .stock import GROUPS, Stock, StockError

bp = Blueprint("web", __name__)

UNIT_CHOICES = tuple(units.UNITS)


def get_stock():
    if "stock" not in g:
        g.conn = db.connect(current_app.config["DATABASE"])
        g.stock = Stock(g.conn, current_app.config["CLOCK"])
    return g.stock


@bp.teardown_app_request
def close_db(_exc):
    conn = g.pop("conn", None)
    if conn is not None:
        conn.close()


def _purchase_json(p):
    return {
        "id": p.id, "food_id": p.food_id, "name": p.name,
        "quantity": units.format_quantity(p.quantity), "unit": p.unit,
        "expiry": p.expiry.isoformat() if p.expiry else None,
        "expiry_display": p.expiry_display, "group": p.group, "expired": p.expired,
    }


def _record(fields):
    return get_stock().record_purchase(
        fields.get("name"), fields.get("quantity"), fields.get("unit"),
        fields.get("expiry"), fields.get("group"),
    )


@bp.post("/api/purchases")
def api_record_purchase():
    try:
        purchase_id = _record(request.get_json(silent=True) or {})
    except StockError as e:
        return jsonify(error=str(e)), 400
    return jsonify(id=purchase_id), 201


def _totals_json(totals):
    return [{
        "name": t["name"], "unit": t["unit"],
        "total": units.format_quantity(t["total"]),
        "by_group": {g: units.format_quantity(q) for g, q in t["by_group"].items()},
    } for t in totals]


@bp.get("/api/purchases")
def api_list_purchases():
    try:
        purchases = get_stock().list_purchases(
            request.args.get("group"), request.args.get("q"))
    except StockError as e:
        return jsonify(error=str(e)), 400
    return jsonify([_purchase_json(p) for p in purchases])


@bp.get("/api/totals")
def api_totals():
    return jsonify(_totals_json(get_stock().totals()))


@bp.get("/totals")
def totals_page():
    return render_template("totals.html", totals=_totals_json(get_stock().totals()),
                           groups=GROUPS)


@bp.get("/api/foods")
def api_suggest_foods():
    return jsonify(get_stock().suggest_foods(request.args.get("q", "")))


@bp.get("/")
def index():
    group, search = request.args.get("group", ""), request.args.get("q", "")
    try:
        found = get_stock().list_purchases(group, search)
        error = None
    except StockError as e:
        found, error = [], str(e)
    return render_template("index.html", purchases=[_purchase_json(p) for p in found],
                           groups=GROUPS, group=group, search=search, error=error)


@bp.get("/purchases/new")
def new_purchase():
    return render_template("new_purchase.html", units=UNIT_CHOICES, groups=GROUPS,
                           form={"group": request.args.get("group", "")}, error=None,
                           added=request.args.get("added"))


@bp.post("/purchases")
def create_purchase():
    try:
        _record(request.form)
    except StockError as e:
        return render_template("new_purchase.html", units=UNIT_CHOICES, groups=GROUPS,
                               form=request.form, error=str(e), added=None), 400
    if "again" in request.form:
        return redirect(url_for("web.new_purchase", added=request.form.get("name", "").strip(),
                                group=request.form.get("group", "")))
    return redirect(url_for("web.index"))
