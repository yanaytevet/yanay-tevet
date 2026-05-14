#!/usr/bin/env bash
docker-compose -f ../dockers/docker-compose-dev-infra.yml up --force-recreate -d
./create_backend.sh
