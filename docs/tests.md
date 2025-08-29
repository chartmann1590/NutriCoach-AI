# Testing Guide

This document explains the test suite layout under `tests/`, how to run each category, and conventions to follow when adding new tests.

---

## Structure

```
tests/
  unit/           # Fast, isolated tests for services and pure logic
  integration/    # API/database integration tests
  e2e/            # End-to-end UI flows (requires running server)
  manual/         # Optional/manual scripts for exploratory checks
  conftest.py     # Shared pytest fixtures and config
  seed.py         # Helpers to seed data for tests
```

### Directories

- `unit/`
  - Example: `tests/unit/test_services.py`, `tests/unit/test_models.py`
  - Scope: Single function/class; mock external dependencies.

- `integration/`
  - Example: `tests/integration/test_json_serialization.py`
  - Scope: Interactions across modules and the database or app context.

- `e2e/`
  - Examples: `test_admin.py`, `test_user_journey.py`, `test_complete_application.py`
  - Scope: Full-stack flows; requires the app running and Playwright browsers installed.

- `manual/`
  - Examples: `test_live_api.py`, `final_assessment.py`
  - Scope: Developer-run checks that may hit live/staging servers or require credentials.

---

## Running Tests

From the project root, ensure the virtual environment is active, then:

```bash
# All tests
python -m pytest -v

# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only
python -m pytest tests/integration/ -v

# End-to-end tests (headed UI)
python -m pytest tests/e2e/ -v --headed

# With coverage
python -m pytest --cov=. --cov-report=html
```

You can also use `make` targets:

```bash
make test       # unit + e2e
make test-unit
make test-e2e   # requires Playwright
```

Playwright browsers installation (first run):

```bash
python -m playwright install
```

---

## Conventions

- Name files `test_*.py`; functions `test_*`.
- Keep unit tests fast and deterministic. Mock network and filesystem.
- Prefer realistic fixtures in `conftest.py` and factory helpers.
- When adding integration tests, isolate side-effects and reset the database between tests.
- E2E tests should assert on user-visible outcomes, not implementation details.
- Use markers (e.g., `@pytest.mark.slow`, `@pytest.mark.e2e`) if you introduce long-running suites.

---

## Environment

- Configure `.env` for local testing; defaults target `instance/nutricoach.db`.
- For CI/Docker: run tests inside the container with environment prepared.
- Avoid hardcoding live URLs in committed tests. Place such checks in `tests/manual/`.


