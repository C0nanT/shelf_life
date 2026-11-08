# Shelf Life

Local food stock and expiry tracker (Flask + SQLite). See `.scratch/food-expiry-tracking/SPEC.md`.

## Running on the PC (Docker)

Two services from one image:

- `web`: the page (gunicorn), at <http://127.0.0.1:25080>. It listens only on the PC's loopback and has no login.
- `scheduler`: the daily routine (expiry check, Telegram digest, backup). It runs once when the service starts and every day at 09:00 `America/Sao_Paulo`. Runs share a lock (`flock` on `/data/daily_routine.lock`), so two never overlap.

Both use `restart: unless-stopped`, so they come back when Docker starts at boot.

### First start

    cp .env.example .env              # then fill TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
    mkdir -p /home/conan/Desktop/backups/shelf_life
    docker compose up -d --build

`.env` is git-ignored; `.env.example` documents every variable (including the optional port, backup folder and uid/gid overrides). The backup folder must exist before `up`; compose refuses to start rather than letting Docker create it owned by root. The container runs as uid/gid 1000 (`SHELF_LIFE_UID`/`SHELF_LIFE_GID`), so backup files are owned by you.

### Day to day

    docker compose ps                         # status and health
    docker compose logs -f scheduler          # routine runs and next run time
    docker compose exec scheduler shelf-life-scheduler --once   # run the routine now
    docker compose up -d --build              # after pulling new code

To check the Telegram configuration, send a test message (it always sends, unlike the routine, which only sends when a milestone is due):

    docker compose run --rm --no-deps scheduler python -c \
        "from shelf_life.telegram import TelegramSender; TelegramSender.from_env().send('Stock: test message from Shelf Life')"

### Where the data lives

- **Database**: `/data/shelf_life.db` inside the named Docker volume `shelf_life_data`. It survives `docker compose down`, rebuilds and recreated containers. Only `docker compose down -v` (or `docker volume rm shelf_life_data`) deletes it.
- **Backups**: `/home/conan/Desktop/backups/shelf_life/shelf_life-YYYY-MM-DD.db`, one per day, the 7 most recent kept. They are on the same disk, so they protect against mistakes and a corrupted database, not disk failure.
- **Secrets**: `.env` in the project folder.

### Restoring a backup

Stop both services so nothing writes during the restore, copy the chosen backup over the database, and start again (replace the date):

    docker compose stop
    docker compose run --rm --no-deps scheduler \
        sh -c 'cp /backups/shelf_life-2026-11-08.db /data/shelf_life.db && rm -f /data/shelf_life.db-journal'
    docker compose start

To keep the current database first, copy it out before restoring:

    docker compose run --rm --no-deps scheduler cp /data/shelf_life.db /backups/before-restore.db

(`before-restore.db` does not match the backup name pattern, so retention never deletes it.)

## Development

    python3 -m venv .venv && . .venv/bin/activate
    pip install -r requirements-dev.txt
    flask --app shelf_life run --host 127.0.0.1

The database defaults to `instance/shelf_life.db`; set `SHELF_LIFE_DB` to use another file.

## Test

    python -m pytest

Tests use the Flask test client with a temporary database and a fixed clock (see `tests/base.py`).
