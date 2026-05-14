#!/usr/bin/env bash
set -e

docker compose -f ../dockers/docker-compose-prod.yml run --rm \
  --entrypoint /venv/bin/python \
  yanay_tevet_backend \
  manage.py "$@"

