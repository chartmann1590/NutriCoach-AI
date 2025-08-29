## Deployment

Recommended: Docker Compose with PostgreSQL and Redis.

### Docker Compose
```bash
docker compose up -d
docker compose logs -f app
```

Services (from `docker-compose.yml`):
- `app`: Flask app (port 5001 -> 5000 in container)
- `postgres`: Postgres 15
- `redis`: Redis 7

Key env vars:
- `DATABASE_URL=postgresql://nutricoach:...@postgres:5432/nutricoach`
- `REDIS_URL=redis://redis:6379/0`
- `OLLAMA_URL=http://host.docker.internal:11434` (Mac/Windows Docker)

Volumes:
- `uploads:/app/static/uploads`
- `logs:/app/logs`

### Production Notes
- Put behind Nginx/Traefik with HTTPS and request limits
- Set strong `SECRET_KEY` and `WTF_CSRF_SECRET_KEY`
- Enable `SESSION_COOKIE_SECURE=true` and secure cookies
- Use managed Postgres/Redis, backups and monitoring
- Healthcheck: `GET /api/healthz`

### Non-Docker
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export FLASK_ENV=production
python app.py
```

### OpenAPI & Swagger
- Spec: `/openapi.yaml`
- Docs: `/api/docs`

