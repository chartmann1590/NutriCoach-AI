## Getting Started

This guide helps you run NutriCoach quickly using Docker.

### Prerequisites
- Docker and Docker Compose
- (Optional) Python 3.11+ for local runs
- (Optional) Redis and PostgreSQL if not using Docker

### Quick Start (Docker)
```bash
git clone <your-repo-url>
cd nutrition-ai
docker compose up -d
# App: http://localhost:5001
# API Docs: http://localhost:5001/api/docs
```

### Local Python Setup (alternative)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
export FLASK_ENV=development  # Windows PowerShell: $Env:FLASK_ENV='development'
python app.py
```

### Create Admin User
```bash
python scripts/create_admin.py
# or interactive
python scripts/create_admin_interactive.py
```

### Default URLs
- Main App: http://localhost:5001
- Admin Dashboard: http://localhost:5001/admin/dashboard
- Register: http://localhost:5001/auth/register
- API Docs: http://localhost:5001/api/docs
- Health Check: http://localhost:5001/api/healthz

### First Login Flow
1. Register a user or create an admin via script
2. Complete 4-step onboarding
3. Configure Ollama URL under Settings
4. Start using food logging, coach, and analytics

