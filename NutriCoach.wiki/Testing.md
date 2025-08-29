## Testing

Test layout and commands based on `docs/tests.md` and Makefile.

### Layout
```
tests/
  unit/
  integration/
  e2e/
  manual/
  conftest.py
  seed.py
```

### Commands
```bash
python -m pytest -v
python -m pytest tests/unit -v
python -m pytest tests/integration -v
python -m pytest tests/e2e -v --headed
python -m pytest --cov=. --cov-report=html

python -m playwright install  # first run

make test
make test-unit
make test-e2e
```

### Conventions
- Name `test_*.py`; keep unit tests fast and deterministic
- Mock network/filesystem in unit tests
- E2E should assert user-visible outcomes
- Use markers for long-running suites as needed

