"""Daily routine: one command that checks expiry, sends the digest, then runs
the remaining steps (such as backup) even if sending failed.

    python -m shelf_life.daily_routine

Environment: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SHELF_LIFE_DB (database path).
"""
import logging
import os
import sys
from datetime import date

from . import db, warnings
from .telegram import TelegramSender

log = logging.getLogger(__name__)


def send_warnings(db_path, today, sender):
    """Send one digest of new milestones; save them only after a successful send."""
    conn = db.connect(db_path)
    try:
        due = warnings.due_warnings(warnings.load_candidates(conn), today)
        if not due:
            return
        sender.send(warnings.build_digest(due))
        with conn:
            conn.executemany(
                "UPDATE purchase SET last_warned_milestone = ? WHERE id = ?",
                [(w.milestone, w.purchase_id) for w in due])
    finally:
        conn.close()


def run(today, sender, db_path, extra_steps=()):
    """Run every step; a failing step is logged and does not stop the others.

    Returns True when all steps succeeded.
    """
    steps = [("send warnings", lambda: send_warnings(db_path, today, sender)),
             *[(getattr(s, "__name__", "step"), s) for s in extra_steps]]
    ok = True
    for label, step in steps:
        try:
            step()
        except Exception:
            ok = False
            log.exception("Daily routine step failed: %s", label)
    return ok


def main():
    logging.basicConfig(level=logging.INFO)
    db_path = os.environ.get("SHELF_LIFE_DB", "shelf_life.db")
    db.init_db(db_path)
    try:
        sender = TelegramSender.from_env()
    except Exception:
        log.exception("Telegram is not configured")
        sys.exit(1)
    sys.exit(0 if run(date.today(), sender, db_path) else 1)


if __name__ == "__main__":
    main()
