# Scripts Guide

This document describes the maintenance and utility scripts located in `scripts/` and how to use them safely in development and admin workflows.

---

## Directory

- `scripts/create_admin.py` – Create a new admin user quickly
- `scripts/create_admin_interactive.py` – Step-by-step, interactive admin creation
- `scripts/create_admin_with_profile.py` – Create an admin user and an initial profile in one run
- `scripts/make_admin.py` – Promote an existing user account to admin
- `scripts/migrate_db.py` – Database maintenance/migration helper

> Note: Ensure your virtual environment is active and `.env` is configured before running scripts.

---

## Prerequisites

1. Activate the project virtual environment
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
2. Configure environment variables in `.env` (see `README.md` and `.env.example`).
3. The application should be able to initialize via `app.py` with your configured database (default SQLite at `instance/nutricoach.db`).

---

## Usage

Run scripts with the project Python interpreter so they execute in the correct environment:

```bash
# Windows
venv\Scripts\python.exe scripts/create_admin.py

# macOS/Linux
venv/bin/python scripts/create_admin.py
```

Replace the script name as appropriate:

- Interactive creation:
  ```bash
  venv/bin/python scripts/create_admin_interactive.py
  ```
- Create admin with profile scaffold:
  ```bash
  venv/bin/python scripts/create_admin_with_profile.py
  ```
- Promote existing user to admin:
  ```bash
  venv/bin/python scripts/make_admin.py
  ```
- Run database maintenance/migration helper:
  ```bash
  venv/bin/python scripts/migrate_db.py
  ```

Some scripts may prompt for input if credentials or options are not provided. Run them from the project root so relative imports work.

---

## Tips

- Back up `instance/nutricoach.db` before running destructive operations.
- For Docker-based setups, run scripts inside the app container where the environment is pre-configured.
- Keep admin credentials secure and rotate them for production environments.


