# Shelf Life

Local food stock and expiry tracker (Flask + SQLite). See `.scratch/food-expiry-tracking/SPEC.md`.

## Setup

    python3 -m venv .venv && . .venv/bin/activate
    pip install -r requirements-dev.txt

## Run

    flask --app shelf_life run --host 127.0.0.1

## Test

    python -m pytest

Tests use the Flask test client with a temporary database and a fixed clock (see `tests/base.py`).
