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


@bp.get("/api/purchases")
def api_list_purchases():
    return jsonify([_purchase_json(p) for p in get_stock().list_purchases()])


@bp.get("/api/foods")
def api_suggest_foods():
    return jsonify(get_stock().suggest_foods(request.args.get("q", "")))


@bp.get("/")
def index():
    purchases = [_purchase_json(p) for p in get_stock().list_purchases()]
    return render_template("index.html", purchases=purchases)


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


def _remove(fields):
    purchase_id = fields.get("purchase_id")
    try:
        purchase_id = int(purchase_id) if purchase_id not in (None, "") else None
    except (TypeError, ValueError):
        raise StockError("Purchase must be a number") from None
    get_stock().record_removal(
        fields.get("name"), fields.get("quantity"), fields.get("unit"),
        fields.get("reason"), purchase_id,
    )


def _removal_page(form, error):
    purchases = [_purchase_json(p) for p in get_stock().list_purchases()]
    return render_template("new_removal.html", units=UNIT_CHOICES, form=form,
                           purchases=purchases, error=error)


@bp.post("/api/removals")
def api_record_removal():
    try:
        _remove(request.get_json(silent=True) or {})
    except StockError as e:
        return jsonify(error=str(e)), 400
    return jsonify(ok=True), 201


@bp.get("/api/removals")
def api_list_removals():
    return jsonify(get_stock().list_removals())


@bp.get("/history")
def history():
    return render_template("history.html", removals=get_stock().list_removals())


@bp.get("/removals/new")
def new_removal():
    return _removal_page(request.args, None)


@bp.post("/removals")
def create_removal():
    try:
        _remove(request.form)
    except StockError as e:
        return _removal_page(request.form, str(e)), 400
    return redirect(url_for("web.history"))
