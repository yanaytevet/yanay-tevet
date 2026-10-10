#!/usr/bin/env bash
# Stops postgres and redis but keeps their containers and the network. `down` would remove the network, and
# the app containers, which are only stopped, would then refuse to start: `up -d` fails with "network ... not
# found" until they are recreated. Data lives in volumes either way.
docker-compose -f ../dockers/docker-compose-dev-infra.yml stop
