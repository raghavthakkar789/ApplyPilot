#!/bin/sh
set -eu

cd "$(dirname "$0")/.."

if grep -E 'compose[[:space:]]+run[^#]*[[:space:]]web[[:space:]]+pnpm' Makefile; then
  echo "Canonical Make targets must not invoke pnpm in the production web image." >&2
  exit 1
fi

if grep -E 'compose[[:space:]]+run[^#]*[[:space:]]worker[[:space:]]+uv[[:space:]]+run' Makefile; then
  echo "Canonical Make targets must not invoke worker lint or tests in the production worker image." >&2
  exit 1
fi

if ! grep -q 'web-test pnpm lint' Makefile; then
  echo "make lint must run frontend lint through the web-test service." >&2
  exit 1
fi

if ! awk '/^FROM .* AS runner$/,0' apps/web/Dockerfile | grep -q 'CMD \["node", "server.js"\]'; then
  echo "The production web runner stage is missing." >&2
  exit 1
fi

if awk '/^FROM .* AS runner$/,0' apps/web/Dockerfile | grep -qi pnpm; then
  echo "The production web runner must not install pnpm or lint tooling." >&2
  exit 1
fi

if ! grep -q 'FROM deps AS test' apps/web/Dockerfile; then
  echo "The web Dockerfile must keep a dedicated test target." >&2
  exit 1
fi

if ! grep -q 'FROM base AS test' apps/worker/Dockerfile; then
  echo "The worker Dockerfile must keep a dedicated test target." >&2
  exit 1
fi

default_config="$(docker compose config)"
if printf '%s\n' "$default_config" | grep -Eq '^  web-test:|^  worker-test:|^  api-test:|^  postgres-test:'; then
  echo "Test-profile services leaked into the default Compose config." >&2
  exit 1
fi

published="$(printf '%s\n' "$default_config" | awk '/published:/{print}')"
if [ "$(printf '%s\n' "$published" | wc -l)" -ne 1 ]; then
  echo "Default Compose must publish exactly one host port." >&2
  exit 1
fi
if ! printf '%s\n' "$default_config" | grep -q '127.0.0.1'; then
  echo "Default Compose must bind the published port to 127.0.0.1." >&2
  exit 1
fi
if ! printf '%s\n' "$published" | grep -q '3000'; then
  echo "Default Compose must publish only port 3000." >&2
  exit 1
fi

test_config="$(docker compose --profile test config)"
for service in web-test worker-test api-test; do
  if ! printf '%s\n' "$test_config" | grep -q "^  ${service}:"; then
    echo "Test profile is missing ${service}." >&2
    exit 1
  fi
done

web_test_ports="$(printf '%s\n' "$test_config" | awk '
  $0 ~ /^  web-test:/ {in_service=1; next}
  in_service && $0 ~ /^  [A-Za-z0-9_-]+:/ {exit}
  in_service && /published:/ {print}
')"
if [ -n "$web_test_ports" ]; then
  echo "web-test must not publish a host port." >&2
  exit 1
fi

echo "Canonical lint runtime check passed."
