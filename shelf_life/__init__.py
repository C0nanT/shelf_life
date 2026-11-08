import os
from datetime import date

from flask import Flask

from . import db


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(
        DATABASE=os.environ.get("SHELF_LIFE_DB")
        or os.path.join(app.instance_path, "shelf_life.db"),
        CLOCK=date.today,
    )
    if config:
        app.config.update(config)
    os.makedirs(os.path.dirname(os.path.abspath(app.config["DATABASE"])), exist_ok=True)
    db.init_db(app.config["DATABASE"])

    @app.template_filter("br_date")
    def br_date(value):
        """Format an ISO date string (or date) as DD/MM/YYYY."""
        if not value:
            return ""
        if isinstance(value, str):
            value = date.fromisoformat(value[:10])
        return value.strftime("%d/%m/%Y")

    from . import web
    app.register_blueprint(web.bp)
    return app
