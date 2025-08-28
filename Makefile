.PHONY: help venv install dev test lint format clean up down

VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

help:
	@echo "Available commands:"
	@echo "  venv       - Create virtual environment"
	@echo "  install    - Install dependencies"
	@echo "  dev        - Run development server"
	@echo "  test       - Run all tests"
	@echo "  test-unit  - Run unit tests only"
	@echo "  test-e2e   - Run end-to-end tests with Playwright"
	@echo "  lint       - Run linting checks"
	@echo "  format     - Format code with black and isort"
	@echo "  clean      - Clean up temporary files"
	@echo "  up         - Start Docker containers"
	@echo "  down       - Stop Docker containers"

venv:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -r requirements.txt
	$(PYTHON) -m playwright install

dev:
	$(PYTHON) app.py

test: test-unit test-e2e

test-unit:
	$(PYTHON) -m pytest tests/unit/ -v

test-e2e:
	$(PYTHON) -m pytest tests/e2e/ -v --headed

lint:
	$(PYTHON) -m flake8 . --exclude=$(VENV)
	$(PYTHON) -m black --check .
	$(PYTHON) -m isort --check-only .

format:
	$(PYTHON) -m black .
	$(PYTHON) -m isort .

clean:
	rm -rf __pycache__ .pytest_cache .coverage
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

up:
	docker-compose up -d

down:
	docker-compose down

seed:
	$(PYTHON) seed.py

# Windows compatibility
ifeq ($(OS),Windows_NT)
	PYTHON = $(VENV)/Scripts/python.exe
	PIP = $(VENV)/Scripts/pip.exe
endif