#!/bin/sh
set -eu

tracked_env_files="$(git ls-files | awk '/(^|\/)\.env($|\.)/ && $0 !~ /\.env\.example$/')"
if [ -n "$tracked_env_files" ]; then
  echo "Committed environment file detected:" >&2
  echo "$tracked_env_files" >&2
  exit 1
fi

if rg -n 'NEXT_PUBLIC_[A-Z0-9_]*(SECRET|TOKEN|PASSWORD|KEY|DATABASE|PEPPER)|NEXT_PUBLIC_USER_' \
  --glob '!scripts/check-security-boundaries.sh' .; then
  echo "Frontend-public backend secret variable detected." >&2
  exit 1
fi

if rg -n 'USER_PASSWORD|PASSWORD_RESET_PHRASE|OWNER_PASSWORD|GET_PASSWORD|RECOVERY_PHRASE' \
  --glob '.env.example' --glob 'apps/web/**' --glob '!apps/web/tests/**' .; then
  echo "Recoverable-password or owner-secret variable detected in committed config or frontend." >&2
  exit 1
fi

allowed_names='^(POSTGRES_DB|POSTGRES_USER|POSTGRES_PASSWORD|DATABASE_URL|APP_ENV|LOG_LEVEL|DOCUMENT_STORAGE_ROOT|ALLOWED_ORIGIN|COOKIE_SECURE)='
if grep -Ev '^(#|[[:space:]]*$)' .env.example | grep -Ev "$allowed_names"; then
  echo ".env.example contains a non-runtime or owner-data variable." >&2
  exit 1
fi

if rg -ni '(owner[_-]?(name|email|phone|address)|user[_-]?(name|email|password)|password[_-]?reset[_-]?phrase|resume[_-]?(content|text)|forgot[_-]?password|get[_-]?password|recovery[_-]?phrase|session[_-]?token|csrf[_-]?token)=' .env.example; then
  echo ".env.example contains prohibited owner, recovery, or token data." >&2
  exit 1
fi

if git grep -nE '@(gmail|outlook|hotmail|yahoo)\.' -- ':!.git' >/dev/null; then
  echo "Committed file contains a private email-like value." >&2
  git grep -nE '@(gmail|outlook|hotmail|yahoo)\.' -- ':!.git' >&2
  exit 1
fi

echo "Security-boundary scan passed."
