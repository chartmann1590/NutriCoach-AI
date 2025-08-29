## Architecture

High-level overview of NutriCoach components and how they interact.

### Components
- Backend: Flask 3 app with blueprints in `routes/` and REST API in `api/`
- Services: Business logic and integrations in `services/`
- Data: SQLAlchemy models in `models.py` (User, Profile, Settings, FoodLog, FoodItem, CoachMessage, Photo, WeighIn, WaterIntake, SystemLog, GlobalSettings)
- Frontend: Jinja templates in `templates/` with Bootstrap and minimal JS/AJAX/SSE
- Background: APScheduler for reminders (`services/reminder_scheduler.py`)
- Sessions/Cache: Redis via `Flask-Session`
- Mobile: Flutter client in `nutrition_ai_mobile/`

### App Initialization
- `app.py#create_app` loads config, initializes extensions (`extensions.py`), registers blueprints, sets up Redis, CSRF, and scheduler, serves `/openapi.yaml` and `/api/docs`.

### Blueprints
- `routes.auth` – login/register
- `routes.main` – dashboard
- `routes.onboarding` – 4-step setup
- `routes.settings` – user preferences, Ollama config
- `routes.coach` – AI chat (SSE)
- `routes.admin` – admin pages
- `api.routes` – JSON REST API

### Services Layer
- `OllamaClient` – local LLM interface; chat streaming, vision analysis, model list/pull, connectivity test
- `NutritionSearch` – Open Food Facts + Wikipedia search, barcode lookup, nutrition estimates
- `FoodParser` – Normalizes vision results, enriches with nutrition
- `RecommendationService` – daily/weekly summaries, meal suggestions
- `AnalyticsService` – trends, distributions, top foods, export
- `VisionClassifier` – image preprocessing/feature extraction
- `NotificationService` – user/admin notifications

### Data Flow (Photo Recognition)
1. Client uploads image to `/api/photo/upload`
2. Server stores file under `static/uploads/food` and processes image
3. Vision analysis via `OllamaClient.vision_analyze`
4. `FoodParser` enriches candidates with nutrition data
5. Response returns candidates with nutrition and references

### Security
- CSRF protection on forms; API CSRF-exempt but session-authenticated
- BCrypt password hashing; role-based admin
- File upload validation and size limits

### Diagrams (conceptual)
- Frontend (Jinja) ↔ API (`/api/*`) ↔ Services ↔ DB/Redis/Ollama

