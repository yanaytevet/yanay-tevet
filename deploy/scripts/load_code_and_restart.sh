#!/usr/bin/env bash
git pull origin main
./rebuild.sh
./start_prod.sh
docker builder prune -f --reserved-space 5GB