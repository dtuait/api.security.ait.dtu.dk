# syntax=docker/dockerfile:1.7

# Base image: CPython 3.12 on Debian bookworm
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# System dependencies required by the project
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        gcc \
        g++ \
        git \
        gnupg \
        libffi-dev \
        libldap2-dev \
        libmariadb-dev-compat \
        libpq-dev \
        libsasl2-dev \
        libssl-dev \
        libxml2-dev \
        libxslt1-dev \
        netcat-openbsd \
        pkg-config \
        tzdata \
        unixodbc \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Add upstream PostgreSQL apt repo and install client/server (optional)
RUN install -d /usr/share/postgresql-common/pgdg \
    && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
        | gpg --dearmor -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.gpg \
    && chmod 0644 /usr/share/postgresql-common/pgdg/apt.postgresql.org.gpg \
    && . /etc/os-release \
    && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.gpg] http://apt.postgresql.org/pub/repos/apt ${VERSION_CODENAME}-pgdg main" \
        > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-16 \
        postgresql-client-16 \
        postgresql-contrib-16 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --system django \
    && useradd --system --gid django --home /home/django --shell /bin/bash django \
    && mkdir -p /home/django \
    && chown -R django:django /home/django

WORKDIR /app

# Python dependencies for the 3.12 + Django 5.1.1 toolchain archived here
# When building with the repository root as context, copy from the archive path
COPY .devcontainer/.docker-image-builder-archive/__owner__dtuait__project__api-security-ait-dtu-dk__image__app-main__tag__python-3.12-bookworm-django-5.1.1-postgres-16-04-10-2025/requirements.txt /tmp/requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# Entrypoint
COPY .devcontainer/.docker-image-builder-archive/__owner__dtuait__project__api-security-ait-dtu-dk__image__app-main__tag__python-3.12-bookworm-django-5.1.1-postgres-16-04-10-2025/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy the full project source into the image so manage.py exists at runtime
COPY . /app
RUN chown -R django:django /app

USER django

ENV PATH="/home/django/.local/bin:${PATH}" \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=app.settings \
    GUNICORN_CMD_ARGS="--workers 3 --timeout 120 --graceful-timeout 30" \
    POSTGRES_DATA_DIR=/var/lib/postgresql/16/main

WORKDIR /app/app-main

EXPOSE 8121 5432

# Healthcheck aligned with project route: /healthz/
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=5 \
    CMD curl -fsS http://127.0.0.1:8121/healthz/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8121"]
