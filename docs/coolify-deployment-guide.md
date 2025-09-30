# Coolify Deployment Guide

This guide walks through deploying the API Security Django application to a self-hosted [Coolify](https://coolify.io/) instance. Coolify uses Docker Compose behind the scenes, so the repository ships with everything you need for a reproducible deployment.

## 1. Prerequisites

Before you begin, make sure you have:

- A running Coolify v3+ installation with access to the **Docker Compose** application type.
- Traefik configured as Coolify's reverse proxy (Coolify sets this up automatically). Have an FQDN ready and pointed at your Coolify host via DNS.
- SSH access or a Git integration (GitHub, GitLab, Bitbucket, or a generic Git URL) so Coolify can pull this repository.
- Application secrets, directory credentials, and API tokens for the data sources you plan to use (see [Environment variables](#2-prepare-environment-variables)).

## 2. Prepare environment variables

The project reads its configuration from environment variables. Copy `.env.example` in the repository to `.env` to review the available settings and gather the values you will need. In Coolify you will create the same keys under **Settings → Environment Variables** for the application.

At minimum set the following values:

| Variable | Purpose |
| --- | --- |
| `SERVICE_FQDN_WEB` | Public hostname (e.g., `api.security.ait.dtu.dk`). |
| `SERVICE_URL_WEB` | Public URL with scheme (e.g., `https://api.security.ait.dtu.dk`). |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames served by Django. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Should include `SERVICE_URL_WEB`. |
| `DJANGO_CSRF_COOKIE_DOMAIN` | Cookie domain; often same as `SERVICE_FQDN_WEB`. |
| `DJANGO_SESSION_COOKIE_SECURE`, `DJANGO_CSRF_COOKIE_SECURE`, `DJANGO_SECURE_SSL_REDIRECT` | Production security flags (defaults true). |
| `DJANGO_SECRET` | A long random string used for Django's cryptographic signing. (required) |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Credentials for PostgreSQL. (required: `POSTGRES_PASSWORD`) |
| `TRAEFIK_HOST` | FQDN that Traefik should route to this application. |
| `TRAEFIK_NETWORK`, `TRAEFIK_ENTRYPOINT`, `TRAEFIK_CERTRESOLVER` | Networking metadata; defaults match a standard Coolify install. Override if your Traefik setup differs. |
| `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD` | Credentials you will use to create an administrative user after deployment. |

All of the other entries in `.env.example` are optional or relate to integrations (Azure AD, SCCM, Microsoft Defender, OpenAI, etc.). Populate them as needed for your environment.

> **Tip:** Leave `DJANGO_DEBUG=false` in production and keep `DJANGO_SESSION_COOKIE_SECURE`, `DJANGO_CSRF_COOKIE_SECURE`, and `DJANGO_SECURE_SSL_REDIRECT` set to `true` to enforce HTTPS-only cookies.

## 3. Add the application in Coolify

1. In Coolify, click **New Application → Docker Compose**.
2. Choose the Git provider and repository that hosts this project, then select the branch you want to deploy (typically `main`).
3. When prompted for the compose file path, enter `docker-compose.coolify.yml`. Leave the working directory as `/` unless you have the repository nested deeper.
4. Coolify will detect the services defined in the compose file:
   - `web`: Builds from the repository `Dockerfile`, runs Gunicorn on port `8121`, and exposes the Django app. It mounts persistent volumes for `/data/static` and `/data/media`.
   - `db`: Uses the official `postgres:16` image with a persistent volume for the database cluster.
5. Under the **Environment Variables** tab, add the keys discussed above (copy/paste from your `.env`). You can bulk import by pasting the contents of your `.env` file.
6. Ensure the Traefik network name matches your setup. By default the compose file expects an external network named `coolify-network`. Adjust the `TRAEFIK_NETWORK` variable if your Traefik network is different, or create the network beforehand. On a raw Docker host (for example when rehearsing locally) run `docker network create coolify-network` once to satisfy the external network reference. Coolify creates `coolify-network` automatically when Traefik is enabled.


## 4. First deployment

1. Click **Deploy**. Coolify will:
   - Build the application image using the provided `Dockerfile` (installs system packages, Python dependencies, and copies the project code).
   - Launch PostgreSQL and wait for it to become healthy.
   - Start the Django container, which runs `manage.py migrate` and `collectstatic` automatically via `docker/entrypoint.sh`.
2. Watch the deployment logs to ensure migrations complete successfully and that Gunicorn is listening on port `8121`.
3. Once Traefik provisions a certificate and routes traffic, browse to `https://<your-domain>` to confirm the site is online.

## 5. Create an administrative user

If no superuser exists yet, open the Coolify application page, go to the **Actions → Execute Command** menu for the `web` service, and run:

```bash
python manage.py createsuperuser --username "$DJANGO_SUPERUSER_USERNAME" --email you@example.com
```

Provide the same password you configured in the environment variables when prompted. You can now log in to the admin interface and configure integrations.

## 6. Ongoing management

- **Updating the application:** Push new commits to the tracked branch and trigger a redeploy in Coolify. The entrypoint will re-run migrations and collect static assets as needed.
- **Running management commands:** Use Coolify's “Execute Command” feature on the `web` container to run scripts such as `python manage.py shell` or custom management commands.
- **Backups:** The compose file defines named volumes (`postgres_data`, `static_data`, `media_data`). Configure backups for these volumes in your Coolify host to protect database and media content.

## 7. Local smoke test (optional)

You can rehearse the deployment locally with Docker Compose to verify your configuration before pushing to production:

```bash
cp .env.example .env
# Edit .env with the values you plan to use
docker network create coolify-network  # satisfies the external Traefik network dependency
docker compose -f docker-compose.coolify.yml up --build
```

If you already have a differently named Traefik network, skip the `docker network create` command and export `TRAEFIK_NETWORK=<your-network>` before running Compose. The stack will come up exactly as Coolify orchestrates it, so you can validate migrations, networking, and integrations ahead of time.

## 8. Troubleshooting

### `network coolify-network declared as external, but could not be found`

This error appears when Docker cannot find the Traefik network referenced by the compose file. On Coolify hosts the network is
usually created automatically, but if you see this message:

```
network coolify-network declared as external, but could not be found
```

SSH into the Coolify server and create the network once:

```bash
docker network create coolify-network
```

If your Traefik installation uses a different network name, set the `TRAEFIK_NETWORK` environment variable in Coolify to that
name instead of creating `coolify-network`.
