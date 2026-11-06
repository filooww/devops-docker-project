# devops-docker-project

A small Flask web app packaged with Docker and run with Docker Compose behind an Nginx reverse proxy. The project has two profiles: `dev` (plain HTTP) and `prod` (HTTPS with a self-signed certificate generated at image build time).

## Project structure

```
docker-app/
├── app/
│   ├── app.py              # Flask app: "/" page and "/health" endpoint
│   └── requirements.txt
├── nginx/
│   ├── Dockerfile          # multi-stage: certs → dev → prod
│   ├── dev.conf            # HTTP reverse proxy
│   └── prod.conf           # HTTP → HTTPS redirect + TLS reverse proxy
├── Dockerfile              # Flask app image (multi-stage)
├── docker-compose.yaml     # services, profiles, shared extensions
├── .env.dev.example
├── .env.prod.example
├── .dockerignore
└── .gitignore
```

## How to run

Create env files from the examples:

```bash
cp .env.dev.example .env.dev
cp .env.prod.example .env.prod
```

**Dev** (HTTP):

```bash
docker-compose --profile dev up -d --build
```

Open http://localhost

**Prod** (HTTPS):

```bash
docker-compose --profile prod up -d --build
```

Open https://localhost. HTTP requests are redirected to HTTPS. The certificate is self-signed, so the browser shows a warning.

Stop everything:

```bash
docker-compose --profile dev --profile prod down --remove-orphans
```

## Profiles

| | dev | prod |
|---|---|---|
| App service | `app-dev` | `app-prod` |
| Nginx service | `nginx-dev` (target `dev`) | `nginx-prod` (target `prod`) |
| Env file | `.env.dev` | `.env.prod` |
| Ports | `80` | `80` → redirect, `443` HTTPS |
| TLS | no | self-signed certificate |

Common settings for each pair of services are defined once in `x-app-common` and `x-nginx-common` and reused with YAML anchors (`<<: *app-common`).

## Configuration

| Variable | Description |
|---|---|
| `APP_NAME` | App name shown on the page |
| `APP_ENV` | Environment name (`development`, `production`) |
| `PORT` | Port Flask listens on inside the container |

Real `.env.dev` and `.env.prod` are not committed, only the `.example` files.

## Architecture

```
dev:   Browser → :80  → nginx-dev  (HTTP)        ──[backend]──> app:5555 (Flask)
prod:  Browser → :80  → nginx-prod (301 → HTTPS)
       Browser → :443 → nginx-prod (TLS)         ──[backend]──> app:5555 (Flask)
```

- **Reverse proxy**: Nginx is the only service with published ports. Flask is reachable only through Nginx.
- **DNS between containers**: both app services have the network alias `app`, so Nginx always proxies to `http://app:5555` regardless of the profile.
- **Isolated network**: the app runs only in the `backend` network, marked `internal: true`.
- **Custom Nginx image**: multi-stage build. The `certs` stage generates a self-signed certificate with OpenSSL, the `prod` stage copies the ready certificate into the image, the `dev` stage has no TLS.
- **Startup order**: each Nginx waits until its app is healthy (`depends_on` with `service_healthy`).

## Security

| Setting | Effect |
|---|---|
| Non-root users | Flask runs as `app`, Nginx as `nginx` (unprivileged image) |
| `read_only: true` | Read-only container file systems, `/tmp` is a tmpfs |
| `cap_drop: [ALL]` | All Linux capabilities are removed |
| `no-new-privileges` | Processes cannot gain extra privileges |
| CPU and memory limits | App: 0.5 CPU / 256 MB, Nginx: 0.25 CPU / 64 MB |
| Pinned images | `python:3.12-slim`, `nginxinc/nginx-unprivileged:1.27-alpine`, `alpine:3.20` |

> The self-signed certificate is baked into the image for demo purposes. In real production, use a trusted certificate (for example Let's Encrypt) and pass it to the container through secrets or a volume instead of storing the private key in the image.

## Useful commands

| Command | What it does |
|---|---|
| `docker-compose --profile prod ps` | Check container status and health |
| `docker-compose --profile prod logs -f nginx-prod` | Follow Nginx logs |
| `curl -I http://localhost` | Check the HTTP → HTTPS redirect in prod |
| `curl -k https://localhost` | Open the app over HTTPS, ignoring the self-signed certificate |
| `docker-compose exec nginx-prod getent hosts app` | Check DNS resolution of the app |
| `docker stats --no-stream` | Check CPU and memory limits |

## Screenshots

Running containers:

![docker ps](screenshots/docker-ps.png)

App in the browser:

![app](screenshots/app.png)
