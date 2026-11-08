"""Backup: consistent copy of the database plus retention."""
import os
import re
import sqlite3

KEEP = 7
PREFIX = "shelf_life-"
_NAME = re.compile(r"^shelf_life-\d{4}-\d{2}-\d{2}\.db$")


def file_name(day):
    return f"{PREFIX}{day.isoformat()}.db"


def back_up(db_path, dest_dir, today, keep=KEEP):
    """Save one copy for `today` (replacing any earlier one that day), keep the newest `keep`.

    Uses SQLite's online backup API, so the copy is consistent while the
    service is writing. Returns the path of the copy.
    """
    os.makedirs(dest_dir, exist_ok=True)
    final = os.path.join(dest_dir, file_name(today))
    partial = final + ".partial"
    src = sqlite3.connect(db_path)
    dst = sqlite3.connect(partial)
    try:
        src.backup(dst)
    except Exception:
        dst.close()
        dst = None
        os.unlink(partial)
        raise
    finally:
        src.close()
        if dst is not None:
            dst.close()
    os.replace(partial, final)
    _apply_retention(dest_dir, keep)
    return final


def _apply_retention(dest_dir, keep):
    copies = sorted(n for n in os.listdir(dest_dir) if _NAME.match(n))
    for name in copies[:-keep]:
        os.unlink(os.path.join(dest_dir, name))
