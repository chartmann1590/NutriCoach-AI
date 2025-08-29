## API Reference

Interactive docs: `http://localhost:5001/api/docs` (Swagger UI)
Spec: `http://localhost:5001/openapi.yaml`

### Authentication
- Cookie-based session auth; login via web app. All endpoints require auth except `/api/healthz`.

### Core Endpoints
- Health: `GET /api/healthz`
- Food Logs:
  - `GET /api/logs?date=YYYY-MM-DD&limit=50`
  - `POST /api/logs` with JSON `{ custom_name, meal, grams, calories, ... }`
  - `DELETE /api/logs/{id}`
- Nutrition Search:
  - `GET /api/search_nutrition?q=apple`
  - `GET /api/search_barcode?barcode=...`
- Photo Analysis:
  - `POST /api/photo/upload` (multipart form-data, field `photo`)
- AI Coach:
  - `POST /api/coach/chat` – Server-Sent Events stream (text/plain)
  - `DELETE /api/coach/clear-history`
  - `GET /api/coach/history`
- Health Tracking:
  - `POST /api/weigh-in` `{ weight_kg }`
  - `POST /api/water-intake` `{ ml }`
- Analytics:
  - `GET /api/analytics/nutrition-trends?days=30`
  - `GET /api/analytics/weight-trends?days=90`
  - `GET /api/analytics/dashboard`
- Export:
  - `GET /api/export/logs.csv?from=YYYY-MM-DD&to=YYYY-MM-DD`
- Models:
  - `GET /api/models/list`
  - `POST /api/models/pull` `{ model }`
- Settings:
  - `POST /api/settings/test_ollama` `{ ollama_url }`
- Notifications:
  - `GET /api/notifications?limit=20&offset=0&unread_only=false`
  - `GET /api/notifications/counts`
  - `POST /api/notifications/{id}/mark-read`
  - `POST /api/notifications/mark-all-read`
  - `DELETE /api/notifications/{id}`
  - `POST /api/notifications/{id}/dismiss`

### Response Shape
Unless streaming, responses are JSON with a `data` or direct fields, or `error` on failure. CSV download for export.

### Rate Limits
Basic server-side limits; deploy behind a reverse proxy for production throttling.

