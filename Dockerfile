# syntax=docker/dockerfile:1

FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
        ca-certificates \
        apt-transport-https \
    && curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null \
    && echo "deb [arch=amd64] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/microsoft-prod.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        git \
        libpq-dev \
        libsasl2-dev \
        libldap2-dev \
        libssl-dev \
        pkg-config \
        libffi-dev \
        libxml2-dev \
        libxslt1-dev \
        default-libmysqlclient-dev \
        libmariadb-dev-compat \
        unixodbc \
        unixodbc-dev \
        msodbcsql18 \
        netcat-openbsd \
        tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app-main/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY . /app

RUN groupadd --system django \
    && useradd --system --gid django --home /home/django --shell /bin/bash django \
    && mkdir -p /home/django \
    && chown -R django:django /home/django /app

USER root

ENV PATH="/home/django/.local/bin:${PATH}" \
    PYTHONPATH=/app \
    DJANGO_SETTINGS_MODULE=app.settings \
    GUNICORN_CMD_ARGS="--workers 3 --timeout 120 --graceful-timeout 30 --access-logfile - --error-logfile - --capture-output --log-level info"

WORKDIR /app/app-main

EXPOSE 8121

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8121"]
