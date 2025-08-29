## Troubleshooting

### App won’t start
- Check container logs: `docker compose logs -f app`
- Verify DB/Redis healthchecks are green
- Ensure `SECRET_KEY` and DB URL are set

### Can’t connect to Ollama
- Confirm Ollama runs locally and is reachable
- In Docker, use `http://host.docker.internal:11434`
- Test via `/api/settings/test_ollama`

### Photo analysis returns empty candidates
- Ensure vision model (e.g., `llava`) is pulled and configured
- Check logs for JSON parse errors in vision output

### 401/redirects from API
- Login via web UI; APIs use session cookies
- For mobile, ensure base URL points to the server origin

### Slow queries or logs view
- Use PostgreSQL, add indexes, archive old logs

### File upload errors
- Check `MAX_CONTENT_LENGTH` and allowed extensions

