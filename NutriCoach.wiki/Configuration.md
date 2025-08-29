## Configuration

NutriCoach is configured via environment variables (see example in README).

### Core Settings
- `FLASK_ENV`: `development` | `production`
- `SECRET_KEY`, `WTF_CSRF_SECRET_KEY`: security keys
- `DATABASE_URL`: e.g., `sqlite:///nutricoach.db` or `postgresql://user:pass@host/db`
- `REDIS_URL`: e.g., `redis://localhost:6379/0`
- `UPLOAD_FOLDER`: default `static/uploads`
- `MAX_CONTENT_LENGTH`: default 8MB

### AI (Ollama)
- `OLLAMA_URL`: default `http://localhost:11434`
- `DEFAULT_CHAT_MODEL`: e.g., `llama2`, `mistral`
- `DEFAULT_VISION_MODEL`: e.g., `llava`

### External APIs
- `OPENFOODFACTS_API_URL`: default `https://world.openfoodfacts.org`
- `WIKIPEDIA_API_URL`: default `https://en.wikipedia.org`

### Security Flags
- `OFFLINE_MODE`: `true|false` to avoid external calls
- `DISABLE_EXTERNAL_CALLS`: `true|false` global block for outbound requests

### Logging
- `LOG_LEVEL`: `DEBUG|INFO|WARNING|ERROR`

### Docker Compose
The provided `docker-compose.yml` defines services for the app, database, and redis. Adjust mounted volumes and environment variables for production.

### Production Notes
- Set `SESSION_COOKIE_SECURE=true` behind HTTPS
- Use PostgreSQL and managed Redis
- Rotate secrets, restrict file uploads, enable health monitoring

