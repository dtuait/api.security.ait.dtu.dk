#!/bin/sh
set -e

# Allow overriding the manage.py path if needed
APP_DIR=${APP_DIR:-/app/app-main}
MANAGE_PY="${APP_DIR}/manage.py"

if [ ! -f "$MANAGE_PY" ]; then
  echo "Could not locate manage.py at $MANAGE_PY" >&2
  exit 1
fi

# Wait for the database to become available if POSTGRES_HOST is defined
if [ -n "$POSTGRES_HOST" ]; then
  POSTGRES_PORT=${POSTGRES_PORT:-5432}
  echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
  for _ in $(seq 1 60); do
    if nc -z "$POSTGRES_HOST" "$POSTGRES_PORT" >/dev/null 2>&1; then
      echo "PostgreSQL is available."
      break
    fi
    sleep 2
  done

  if ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT" >/dev/null 2>&1; then
    echo "PostgreSQL did not become available in time." >&2
    exit 1
  fi
fi

cd "$APP_DIR"

if [ "${DJANGO_MIGRATE:-true}" = "true" ]; then
  python manage.py migrate --noinput
fi

if [ "${DJANGO_COLLECTSTATIC:-true}" = "true" ]; then
  python manage.py collectstatic --noinput
fi

exec "$@"

