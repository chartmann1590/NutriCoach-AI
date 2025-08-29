## Development

### Prerequisites
- Python 3.11+
- Redis, PostgreSQL (or use Docker Compose)

### Setup
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env  # if available; otherwise set env vars per README
python app.py
```

### Useful Make Targets
```bash
make format
make lint
make test
make test-unit
make test-e2e
```

### Project Structure
See README for a full tree. Key dirs: `routes/`, `api/`, `services/`, `templates/`, `static/`, `tests/`.

### Code Style
- Python: Black, isort, flake8
- HTML: semantic templates in `templates/`
- JS: ES6+

### Database
- Default SQLite for local (`instance/nutricoach.db`); PostgreSQL for production.
- Migrations via Flask-Migrate:
```bash
flask db init
flask db migrate -m "Description"
flask db upgrade
```

### Running Scripts
See `docs/scripts.md` for details.

