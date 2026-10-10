#!/usr/bin/env bash
# Says whether the local dev stack is up. Runs from anywhere, unlike the other scripts here, because
# Claude Code runs it as a SessionStart hook (.claude/settings.json) and its output becomes context
# for the session; by hand it is `bash deploy/dev_scripts/dev_status.sh`.
#
# The stack runs in Docker, mounted from the main checkout, so it is one stack for every session.
# A worktree session's own files are never what the running servers serve, which is why this reports
# the checkout they do serve and warns when a container is mounted from anywhere else.

main_checkout="$(dirname "$(git -C "$(dirname "$0")" rev-parse --path-format=absolute --git-common-dir)")"
session_checkout="$(git -C "${CLAUDE_PROJECT_DIR:-$PWD}" rev-parse --show-toplevel 2>/dev/null)"
start_command="cd $main_checkout/deploy/dev_scripts && docker-compose -f ../dockers/docker-compose-dev-backend.yml up -d"

if ! docker info >/dev/null 2>&1; then
  echo "Dev stack: DOWN — Docker is not running. Once Docker Desktop is up, start the stack with: $start_command"
  exit 0
fi

# A missing container still makes inspect print an empty line, so test what came back, not the exit code.
container_status() {
  local status
  status="$(docker inspect -f '{{.State.Status}}' "$1" 2>/dev/null | tr -d '[:space:]')"
  echo "${status:-missing}"
}

# Docker Desktop reports some bind sources under /host_mnt; the rest of the path is the host's.
app_mount() {
  docker inspect -f '{{range .Mounts}}{{if eq .Destination "/app"}}{{.Source}}{{end}}{{end}}' "$1" 2>/dev/null \
    | sed 's#^/host_mnt##'
}

http_status() {
  curl -s -o /dev/null -m 3 -w '%{http_code}' "$1"
}

problems=()

for container in yanay_tevet_db yanay_tevet_redis; do
  status="$(container_status "$container")"
  if [ "$status" != "running" ]; then
    problems+=("$container is $status — start it first: cd $main_checkout/deploy/dev_scripts && bash start_dev.sh")
  fi
done

for container in yanay_tevet_backend yanay_tevet_web; do
  status="$(container_status "$container")"
  if [ "$status" != "running" ]; then
    problems+=("$container is $status")
  fi
done

# /api/configurations/ is public, so it answers 200 without a session.
backend_http="$(http_status http://localhost:8001/api/configurations/)"
web_http="$(http_status http://localhost:4201/)"
[ "$backend_http" = "200" ] || problems+=("backend http://localhost:8001 answers $backend_http")
[ "$web_http" = "200" ] || problems+=("frontend http://localhost:4201 answers $web_http (000 right after a start means it is still building)")

for pair in yanay_tevet_backend:yanay_tevet_backend yanay_tevet_web:yanay-tevet-web; do
  container="${pair%%:*}"
  expected="$main_checkout/${pair##*:}"
  mounted="$(app_mount "$container")"
  if [ -n "$mounted" ] && [ "$mounted" != "$expected" ]; then
    problems+=("$container serves $mounted, not the main checkout — recreate it with: $start_command")
  fi
done

if [ ${#problems[@]} -eq 0 ]; then
  echo "Dev stack: LIVE — backend :8001 and frontend :4201, serving $main_checkout."
else
  echo "Dev stack: NOT HEALTHY, serving $main_checkout."
  for problem in "${problems[@]}"; do
    echo "- $problem"
  done
  echo "Start or repair it with: $start_command"
fi
echo "Logs: docker logs yanay_tevet_backend | yanay_tevet_web. Re-check with: bash $main_checkout/deploy/dev_scripts/dev_status.sh"

# ngrok is only needed to test the Claude connector, so its absence is not a problem. The backend reads the
# tunnel URL once per process (mcp_server/config.py), so a tunnel started after the backend needs a restart.
ngrok_url="$(curl -s -m 2 http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)"
if [ -n "$ngrok_url" ]; then
  echo "ngrok: $ngrok_url → MCP connector at $ngrok_url/mcp (docker restart yanay_tevet_backend if the tunnel is newer than the backend)."
fi

if [ -n "$session_checkout" ] && [ "$session_checkout" != "$main_checkout" ]; then
  echo "This session works in $session_checkout, which the running servers do not serve: its edits reach the app only once they are in the main checkout."
fi
exit 0
