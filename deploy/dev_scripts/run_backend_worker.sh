#!/usr/bin/env bash
# Runs a celery worker. With no argument it consumes every queue in yanay_tevet_backend/celery.py; pass a
# comma-separated list to narrow it, e.g. ./run_backend_worker.sh emails
#
# There is no always-on worker in the compose file because nothing in the app enqueues a task today: the only
# task, daily_cleaning, is sent by beat, and settings.py has no CELERY_BROKER_URL yet (it is commented out).
# Set a broker before relying on this.
set -e

QUEUES="${1:-main,emails}"

docker-compose -f ../dockers/docker-compose-dev-backend.yml run --rm \
  --entrypoint /venv/bin/celery \
  yanay_tevet_backend \
  -A yanay_tevet_backend worker -Q "$QUEUES" --concurrency=1 -l INFO
