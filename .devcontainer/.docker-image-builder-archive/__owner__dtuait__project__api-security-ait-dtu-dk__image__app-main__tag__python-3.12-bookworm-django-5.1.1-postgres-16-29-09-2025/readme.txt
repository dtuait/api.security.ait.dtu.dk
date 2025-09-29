Image purpose
-------------
- Builds the app against Python 3.12 on Debian bookworm.
- Installs Django 5.1.1, psycopg 3.1.x and other project dependencies.
- Adds PostgreSQL 16 server + client packages so the container can talk to or host a modern Postgres instance.

Build
-----
    docker build -f .devcontainer/.docker-image-builder-archive/__owner__dtuait__project__api-security-ait-dtu-dk__image__app-main__tag__python-3.12-bookworm-django-5.1.1-postgres-16-29-09-2025/Dockerfile -t app-main:python-3.12-django-5.1-postgres-16 .

Runtime notes
-------------
1. By default the container expects an external PostgreSQL service. Set `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER` and `POSTGRES_PASSWORD` so the entrypoint can run migrations before launching gunicorn.
2. PostgreSQL server binaries are installed. If you want to run an embedded Postgres in the same container, start it separately (e.g. `docker run --init --entrypoint bash ... -c "pg_ctlcluster 16 main start && exec container-cmd"`) before the Django entrypoint runs, or pair this image with the official `postgres:16` service via docker compose.
3. The image exposes `8121` for Django/gunicorn and `5432` in case you proxy the local database port.
4. Healthcheck probes `http://127.0.0.1:8121/health/`; adjust or disable via `--no-healthcheck` or a custom build if your deployment differs.

Upgrading
---------
- Update `requirements.txt` in this directory to pin newer versions (e.g. Django `5.1.x` → `5.2.x`).
- Rebuild the image to pick up upstream Python/Debian security updates.

