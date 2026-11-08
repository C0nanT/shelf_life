#!/bin/sh
# Runs the daily routine once at startup, then every day at 09:00 local time
# (TZ, America/Sao_Paulo). Every run goes through flock on a lock file next to
# the database, so two runs never overlap, even with a manual run via
# `docker compose exec scheduler shelf-life-scheduler --once`.
set -u

LOCK_FILE="${SHELF_LIFE_LOCK:-/data/daily_routine.lock}"
RUN_AT="${SHELF_LIFE_RUN_AT:-09:00}"

run_routine() {
    echo "$(date -Iseconds) daily routine: starting"
    flock --nonblock --conflict-exit-code 75 "$LOCK_FILE" python -m shelf_life.daily_routine
    case $? in
        0) echo "$(date -Iseconds) daily routine: finished" ;;
        75) echo "$(date -Iseconds) daily routine: another run holds the lock, skipped" ;;
        # The failed step is already logged above; the next run retries.
        *) echo "$(date -Iseconds) daily routine: failed (see log above)" ;;
    esac
}

next_run() {
    target=$(date -d "today $RUN_AT" +%s)
    if [ "$(date +%s)" -ge "$target" ]; then
        target=$(date -d "tomorrow $RUN_AT" +%s)
    fi
    echo "$target"
}

run_routine
[ "${1:-}" = "--once" ] && exit 0

while true; do
    target=$(next_run)
    echo "$(date -Iseconds) daily routine: next run at $(date -d "@$target" -Iseconds)"
    # Sleep in short steps and compare with the wall clock, so a PC that was
    # suspended at 09:00 runs the routine on wake instead of a day late.
    while [ "$(date +%s)" -lt "$target" ]; do
        sleep 60
    done
    run_routine
done
