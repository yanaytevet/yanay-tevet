#!/usr/bin/env bash
# Runs celery beat, which enqueues the periodic tasks in yanay_tevet_backend/celery.py's beat_schedule.
# It uses celery's own file-based scheduler: django_celery_beat is in requirements.txt but not in
# INSTALLED_APPS. Nothing needs beat to develop the app — start it only when working on scheduled work itself.
set -e

docker-compose -f ../dockers/docker-compose-dev-backend.yml run --rm \
  --entrypoint /venv/bin/celery \
  yanay_tevet_backend \
  -A yanay_tevet_backend beat -l INFO
