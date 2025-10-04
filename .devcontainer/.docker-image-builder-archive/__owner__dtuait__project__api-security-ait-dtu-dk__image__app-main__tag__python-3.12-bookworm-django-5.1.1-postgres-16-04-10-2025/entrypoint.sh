#!/bin/sh
set -e

# Allow overriding the manage.py path if needed
APP_USER=${APP_USER:-django}
APP_GROUP=${APP_GROUP:-$APP_USER}
APP_DIR=${APP_DIR:-/app/app-main}
MANAGE_PY="${APP_DIR}/manage.py"

# Attempt to discover manage.py automatically when the default location is missing.
if [ ! -f "$MANAGE_PY" ]; then
  for candidate in "$APP_DIR" /app/app-main /app/app_main /app; do
    if [ -n "$candidate" ] && [ -f "$candidate/manage.py" ]; then
      if [ "$candidate" != "$APP_DIR" ]; then
        echo "Detected manage.py at $candidate/manage.py; using that path instead of $MANAGE_PY."
      fi
      APP_DIR="$candidate"
      MANAGE_PY="$candidate/manage.py"
      break
    fi
  done
fi

run_as_app_user() {
  if [ "$(id -u)" = "0" ]; then
    if command -v runuser >/dev/null 2>&1; then
      runuser -u "$APP_USER" -- "$@"
    else
      su -m "$APP_USER" -c "$*"
    fi
  else
    "$@"
  fi
}

ensure_storage_dir() {
  dir="$1"
  if [ -z "$dir" ]; then
    return
  fi
  if [ "$(id -u)" = "0" ]; then
    if mkdir -p "$dir" 2>/dev/null; then
      chown "$APP_USER":"$APP_GROUP" "$dir" 2>/dev/null || true
    else
      echo "Warning: Unable to create storage directory $dir" >&2
    fi
  fi
}

if [ ! -f "$MANAGE_PY" ]; then
  echo "Could not locate manage.py at $MANAGE_PY" >&2
  exit 1
fi

# Create static/media roots when running as root
if [ "$(id -u)" = "0" ]; then
  ensure_storage_dir "${DJANGO_STATIC_ROOT}"
  ensure_storage_dir "${DJANGO_MEDIA_ROOT}"
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
  run_as_app_user python manage.py migrate --noinput
fi

if [ "${DJANGO_COLLECTSTATIC:-true}" = "true" ]; then
  run_as_app_user python manage.py collectstatic --noinput
fi

# Optionally bootstrap an administrative account when credentials are provided.
if [ -n "${DJANGO_ADMIN_USERNAME}" ] && [ -n "${DJANGO_ADMIN_PASSWORD}" ]; then
  run_as_app_user python manage.py ensure_admin_user || true
fi

if [ "$(id -u)" = "0" ]; then
  if command -v runuser >/dev/null 2>&1; then
    exec runuser -u "$APP_USER" -- "$@"
  else
    exec su -m "$APP_USER" -c "$*"
  fi
fi

exec "$@"

