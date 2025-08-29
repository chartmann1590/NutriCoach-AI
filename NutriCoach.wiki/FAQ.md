## FAQ

### Do I need the internet to use NutriCoach?
No. Core AI features work locally using Ollama. Set `OFFLINE_MODE=true` to avoid external calls.

### Where are uploads stored?
Under `static/uploads/food/` (volume-mounted in Docker as `uploads`).

### How do I change the AI model?
Set defaults via env (`DEFAULT_CHAT_MODEL`, `DEFAULT_VISION_MODEL`) and per-user in Settings. Use `/api/models/list` and `/api/models/pull`.

### How do I reset an admin password?
Use admin scripts in `scripts/` or a DB update. See [[Admin-Guide]].

### Can I use SQLite in production?
Not recommended. Use PostgreSQL via Docker Compose.

### What about mobile?
See [[Mobile-App]]. Point the app to your server base URL.

