This is a self documenting REST API Build in Django. The philosophy behind this app is to provide a unified interface that brings together data sources like Active Directory, SCCM, Microsoft Defender, and Cisco Network into a single pane of glass. This foundation enables automation and, more importantly, facilitates informed decision-making through AI-generated lists based on data from these sources.

This app is designed for environments with multiple sub-IT departments, where security restrictions prevent full access to systems like SCCM or Microsoft Defender. For example, a sub-IT department can query SCCM to retrieve a list of all computers in their department, along with the software installed on those computers. This app makes such functionality possible. The web portal offers services through a UI/UX experience built on this app's API. For instance, there is currently a service that allows for MFA resets.



# Features
- [x] Active Directory
- SCCM - still in development
- Microsoft Defender - still in development
- Cisco Network - still in development

# Services
- [x] MFA Reset

## Running with Gunicorn

### Test mode
1. Install dependencies:
   ```bash
   pip install -r app-main/requirements.txt
   ```
2. Start the application with Gunicorn in test mode (auto-reloading on changes):
   ```bash
   gunicorn app.wsgi:application --bind 0.0.0.0:8121 --reload
   ```

## Local development with devcontainers

This repository ships with a [VS Code Dev Container](https://code.visualstudio.com/docs/devcontainers/containers) configuration
in `.devcontainer/`. The default `my-development-docker-compose.yaml` file mirrors the production stack, but keeps the Django
process idle so you can run management commands directly from your IDE. Copy `.devcontainer/.env.example` to
`.devcontainer/.env`, supply the required secrets, and open the folder with the "Dev Containers" VS Code extension to start
developing.

## Deploying with Coolify + Traefik

Coolify can build and run the application directly from this repository using the provided `Dockerfile` and
`docker-compose.coolify.yml` compose descriptor. The compose file wires the Django container to PostgreSQL, exposes the
Gunicorn service to Traefik, and provisions persistent volumes for static and media assets.

1. Create a copy of `.env.example` named `.env` and fill in the values (or add the same key/value pairs as environment
   variables in Coolify). Pay particular attention to `DJANGO_SECRET`, `POSTGRES_*`, and `TRAEFIK_*` values.
2. In Coolify, create a "Docker Compose" application pointing to this repository and select `docker-compose.coolify.yml` as the
   compose file. The default labels assume Traefik uses the `coolify-network` overlay and the `websecure` entrypoint—override
   the `TRAEFIK_*` variables if your installation differs.
3. Coolify will build the image from `Dockerfile`, run database migrations, collect static assets, and expose the site through
   Traefik on the hostname configured by `TRAEFIK_HOST`.

To run the same stack locally without Coolify:

```bash
cp .env.example .env
docker compose -f docker-compose.coolify.yml up --build
```

The web container automatically waits for PostgreSQL, applies migrations, and runs `collectstatic` on startup. Static and
media files persist across deployments via the named volumes defined in the compose file.