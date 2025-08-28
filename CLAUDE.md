# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**NutriCoach** is an AI-powered nutrition tracking web application built with Flask that combines intelligent food recognition, personalized AI coaching, and comprehensive nutrition analytics. The application uses local Ollama LLMs for privacy-first AI processing and supports multiple food logging methods including photo analysis, manual entry, and barcode scanning.

## Common Development Commands

### Environment Setup
```bash
# Create and activate virtual environment (recommended)
make venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install all dependencies including Playwright browsers
make install

# Manual setup alternative
python -m venv venv
pip install -r requirements.txt
python -m playwright install
```

### Development Server
```bash
# Run development server
make dev
# Alternative: python app.py
```

### Testing
```bash
# Run all tests (unit + e2e)
make test

# Run only unit tests
make test-unit
# Alternative: python -m pytest tests/unit/ -v

# Run only end-to-end tests with Playwright
make test-e2e  
# Alternative: python -m pytest tests/e2e/ -v --headed

# Run specific test file
python -m pytest tests/unit/test_auth.py
python -m pytest tests/e2e/test_user_journey.py

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

### Code Quality
```bash
# Run linting checks
make lint

# Format code
make format

# Clean temporary files
make clean
```

### Database Operations
```bash
# Initialize database (done automatically on first run)
python -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all()"

# Seed sample data
make seed
# Alternative: python seed.py

# Database migrations (when using Flask-Migrate)
flask db init        # First time only
flask db migrate -m "Description"
flask db upgrade
```

### Docker Operations
```bash
# Production deployment
make up
# Alternative: docker-compose up -d

# Development with Docker
docker-compose -f docker-compose.dev.yml up

# Stop containers
make down
# Alternative: docker-compose down
```

### Admin Operations
```bash
# Create admin user
python create_admin.py
python make_admin.py
```

## Architecture Overview

### Core Application Structure
- **Flask Application Factory Pattern**: `app.py` creates app with config-based initialization
- **Blueprint-based Routing**: Routes organized into logical blueprints in `routes/` directory
- **SQLAlchemy Models**: All database models defined in single `models.py` file
- **Service Layer**: Business logic isolated in `services/` for external integrations and complex operations
- **Form Validation**: WTForms-based forms in `forms/` directory organized by feature area

### Key Components

#### Database Models (`models.py`)
- **User**: Authentication with admin flag and cascading relationships
- **Profile**: User preferences, goals, dietary restrictions, and lifestyle data
- **Settings**: AI configuration (Ollama URLs, models, system prompts)
- **FoodLog**: Main nutrition logging with meal categorization and comprehensive macro/micronutrients
- **FoodItem**: Cached food database entries from external APIs
- **CoachMessage**: AI chat history with role-based storage
- **Photo**: Food image uploads with AI analysis results
- **WeighIn/WaterIntake**: Health tracking data
- **SystemLog/GlobalSettings**: Admin and system management

#### Services (`services/`)
- **OllamaClient**: Interface to local Ollama AI models for chat and vision
- **NutritionSearch**: Integration with Open Food Facts API and Wikipedia
- **FoodParser**: AI-powered food recognition and nutrition parsing from photos
- **RecommendationService**: Personalized meal suggestions and calorie targets
- **AnalyticsService**: Progress tracking, trend analysis, and data visualization
- **VisionClassifier**: Image processing for food recognition

#### Route Blueprints (`routes/`)
- **main.py**: Dashboard, food logging, progress analytics
- **auth.py**: User registration, login, password management
- **onboarding.py**: 4-step setup wizard (profile, goals, lifestyle, AI settings)
- **settings.py**: User preferences, AI configuration, privacy settings
- **coach.py**: AI chat interface with streaming responses
- **admin.py**: User management, system settings, logs, maintenance

#### API Endpoints (`api/routes.py`)
- RESTful API for AJAX interactions
- Streaming endpoints for AI chat responses
- File upload handling for photo analysis
- Analytics data endpoints for dashboard charts
- CRUD operations for food logs and user data

### External Integrations
- **Ollama**: Local LLM serving for privacy-first AI features
- **Open Food Facts**: Global nutrition database for barcode/search
- **Wikipedia**: Supplementary food information
- **Redis**: Session storage and caching
- **Playwright**: End-to-end testing framework

### Security Features
- **Flask-Login**: Session-based authentication
- **CSRF Protection**: All forms include CSRF tokens via Flask-WTF
- **BCrypt**: Password hashing with salt rounds
- **File Upload Security**: Type validation, size limits, secure file handling
- **Privacy-First**: Local AI processing, offline mode support

### Configuration
- **Environment-based Config**: `config.py` with Development/Production/Testing classes
- **Extension Initialization**: Centralized in `extensions.py`
- **Docker Ready**: Production and development Docker Compose configurations
- **Flexible AI Setup**: Configurable Ollama URLs and models per user

### Testing Strategy
- **Unit Tests**: Individual component testing in `tests/unit/`
- **End-to-End Tests**: Full user journey testing with Playwright in `tests/e2e/`
- **Fixtures**: Centralized test setup in `conftest.py`
- **Test Markers**: Organized test categories for selective running

### Development Workflow
- Use `make` commands for consistent development operations
- Test-driven development with comprehensive unit and E2E coverage  
- Code formatting with Black and import sorting with isort
- Pre-commit hooks available for code quality enforcement
- Docker-first deployment with development override configurations

## Important Notes

- The application is designed for local/self-hosted deployment with emphasis on data privacy
- All AI processing can run locally via Ollama - no external AI API calls required
- Mobile app components exist in `mobile/` and `nutrition-ai-mobile/` directories
- Extensive documentation and screenshots available in `docs/` directory
- Database uses SQLite by default but supports PostgreSQL for production
- Redis is required for session storage and caching

## Key Dependencies and Versions

### Core Framework
- **Flask 3.0.0**: Web framework with factory pattern
- **SQLAlchemy 2.0.23**: Database ORM with modern async support
- **Flask-Login 0.6.3**: Session-based authentication
- **Flask-WTF 1.2.1**: Form handling and CSRF protection
- **Flask-Migrate 4.0.5**: Database migration management

### AI and Image Processing
- **PyTorch 2.1.2 + TorchVision 0.16.2**: Deep learning for vision tasks
- **Pillow 10.1.0**: Image processing and manipulation
- **pyzbar 0.1.9**: Barcode scanning capabilities

### Testing and Quality
- **Playwright 1.40.0**: End-to-end browser testing
- **pytest 7.4.3**: Unit testing framework
- **Black 23.11.0 + isort 5.12.0**: Code formatting and import sorting
- **flake8 6.1.0**: Linting and style checking

## Development Patterns

### Model Relationships and JSON Fields
Many models use JSON fields for flexible data storage:
- **Profile**: `preferences`, `allergies`, `conditions`, `equipment` stored as JSON
- **FoodLog**: `micros` field for micronutrient data
- **Photo**: `analysis` field for AI vision results
- **CoachMessage**: `refs` field for source references
- Use helper methods like `get_preferences()` and `set_preferences()` for JSON handling

### Service Layer Architecture
Services are stateless and handle:
- **External API Integration**: Open Food Facts, Wikipedia
- **AI Model Communication**: Ollama client with retry logic
- **Complex Business Logic**: Nutrition calculations, recommendations
- **Data Processing**: Photo analysis, food parsing

### API Design Patterns
- RESTful endpoints under `/api/` prefix
- Streaming responses for AI chat via Server-Sent Events
- JSON error responses with consistent structure
- CSRF exemption for API routes (handled in app.py:50)

### Configuration Management
Three-tier config system in `config.py`:
- **DevelopmentConfig**: Debug mode, SQLite database
- **ProductionConfig**: Production optimizations, PostgreSQL
- **TestingConfig**: In-memory database, disabled CSRF

### Extension Initialization
Centralized in `extensions.py` with proper app context handling:
- Database, migration, login manager, CSRF, session, scheduler, Redis client
- Background scheduler for maintenance tasks (line 60 in app.py)