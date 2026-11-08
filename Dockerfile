# Shelf Life production image: gunicorn for the page, a scheduler loop for the
# daily routine. Both services in docker-compose.yml run this same image.
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=America/Sao_Paulo \
    SHELF_LIFE_DB=/data/shelf_life.db \
    SHELF_LIFE_BACKUP_DIR=/backups

# tzdata so local time (and date.today()) follows TZ; flock comes with util-linux.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

# The container user matches the host user, so backup files written to the
# bind-mounted folder are owned by that user. /data is created with this owner,
# and the named volume inherits it on first mount.
ARG UID=1000
ARG GID=1000
RUN groupadd --gid "${GID}" app \
    && useradd --uid "${UID}" --gid "${GID}" --no-create-home --shell /usr/sbin/nologin app \
    && mkdir /data /backups \
    && chown "${UID}:${GID}" /data /backups

WORKDIR /app

# Dependencies before code: changing the code does not reinstall anything.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY shelf_life/ shelf_life/
COPY --chmod=755 docker/scheduler.sh /usr/local/bin/shelf-life-scheduler

USER ${UID}:${GID}
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "shelf_life:create_app()"]
