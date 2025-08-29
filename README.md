# NutriCoach 🥗🤖

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

**NutriCoach** is a complete, production-ready AI-powered nutrition tracking web application built with Flask. It combines intelligent food recognition, personalized AI coaching, and comprehensive nutrition analytics with a privacy-first approach. The application features local AI processing via Ollama, comprehensive nutrition tracking, and a companion Flutter mobile app for cross-platform access.

## ✨ Features

### 🤖 **AI-Powered Intelligence**
- **AI Nutrition Coach**: Get personalized advice powered by local Ollama LLMs with default coaching prompts
- **Photo Food Recognition**: Upload food photos for automatic identification and nutrition analysis
- **Smart Meal Suggestions**: Context-aware food recommendations based on your goals and preferences
- **Streaming Chat Interface**: Real-time AI responses using Server-Sent Events
- **Customizable System Prompts**: Personalize AI coaching style while preserving user customizations

### 📊 **Comprehensive Tracking**
- **Multi-Modal Food Logging**: Manual entry, photo upload, or barcode scanning (mobile)
- **Progress Analytics**: Detailed charts and insights into your nutrition trends with export capabilities
- **Goal-Based Targets**: Personalized calorie and macro targets based on your profile
- **Micronutrient Tracking**: Complete nutrition profiling with JSON-based micronutrient storage
- **Meal Categorization**: Organized tracking by breakfast, lunch, dinner, and snacks

### 🔒 **Privacy-First Design**
- **Local AI Processing**: Use your own Ollama instance for complete data privacy - no external AI calls
- **Secure Authentication**: BCrypt password hashing, CSRF protection, and session-based login
- **Role-Based Access Control**: Admin functionality with proper authorization decorators
- **Offline Capability**: Works without external API calls when needed
- **Secure File Handling**: Type validation, size limits, and secure filename handling

### 🎨 **Modern User Experience**
- **Responsive Design**: Mobile-first Bootstrap design that works on all devices
- **Cross-Platform Mobile App**: Flutter companion app for Android, iOS, Web, and Windows
- **Admin Dashboard**: Comprehensive user management and system monitoring tools
- **4-Step Onboarding**: Guided setup for profile, goals, lifestyle, and AI configuration
- **Interactive API Documentation**: Swagger UI with complete API specification

### 📱 **Mobile Application**
- **Flutter Cross-Platform**: Native mobile experience on Android, iOS, Web, and Windows
- **Photo Food Analysis**: Camera integration with AI-powered food recognition
- **Server Configuration**: Flexible API endpoint configuration for different deployments
- **Material Design 3**: Modern UI components with confidence indicators and smooth animations

## 🚀 Quick Start

### Option 2: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd nutrition-ai

# Build and start services
docker compose up -d

# Access the app at http://localhost:5001
# API docs at http://localhost:5001/api/docs
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
WTF_CSRF_SECRET_KEY=your-csrf-secret-key

# Database
DATABASE_URL=sqlite:///nutricoach.db
# For PostgreSQL: postgresql://user:password@localhost/nutricoach

# Ollama Configuration
OLLAMA_URL=http://localhost:11434
DEFAULT_CHAT_MODEL=llama2
DEFAULT_VISION_MODEL=llava

# File Upload Configuration
MAX_CONTENT_LENGTH=8388608  # 8MB
UPLOAD_FOLDER=static/uploads

# External APIs
OPENFOODFACTS_API_URL=https://world.openfoodfacts.org
WIKIPEDIA_API_URL=https://en.wikipedia.org

# Security
OFFLINE_MODE=false
DISABLE_EXTERNAL_CALLS=false

# Logging
LOG_LEVEL=INFO
```

### Ollama Setup

1. **Install Ollama**: Follow instructions at [ollama.ai](https://ollama.ai)

2. **Pull Required Models**:
   ```bash
   # For chat functionality
   ollama pull llama2
   
   # For vision capabilities (optional)
   ollama pull llava
   
   # Alternative models
   ollama pull mistral
   ollama pull codellama
   ```

3. **Configure in App**: Set your Ollama URL in the settings page after registration

## 📱 User Guide

### Getting Started

1. **Register**: Create your account at `/auth/register`
2. **Onboarding**: Complete the 4-step setup wizard:
   - Basic Information (age, height, weight)
   - Goals (activity level, targets)
   - Lifestyle (preferences, allergies, equipment)
   - AI Settings (Ollama configuration)
3. **Dashboard**: View your nutrition overview and quick actions

### Food Logging

#### Manual Entry
- Navigate to "Log Food"
- Enter food name, meal type, and nutrition details
- Save to your daily log

#### Photo Logging
- Go to "Photo Log"
- Upload a food photo
- Review AI-suggested items and portions
- Confirm and save to your log

#### Barcode Scanning
- Use the barcode input on search page
- Enter or scan barcode number
- Select from nutrition database results

#### Search Database
- Use "Food Search" to find items
- Browse Open Food Facts and Wikipedia results
- Add items directly to your food log

### AI Coach

1. **Chat Interface**: Ask questions about nutrition, meal planning, or health goals
2. **Quick Actions**: Use suggested prompts for common questions
3. **Context-Aware**: Coach knows your profile, goals, and recent eating patterns
4. **Smart Suggestions**: Get meal recommendations based on remaining calories

### Progress Tracking

- **Dashboard**: Daily overview with macro breakdowns
- **Progress Page**: Detailed charts and analytics
- **Trends**: Weight, nutrition, and habit tracking over time
- **Export**: Download your data as CSV

## 🔧 Technology Stack

### Backend Framework & Extensions
- **Flask 3.0.0**: Modern Python web framework with application factory pattern
- **SQLAlchemy 2.0.23**: Advanced ORM with modern async support and type hints
- **Flask-Login 0.6.3**: Session-based authentication and user management
- **Flask-WTF 1.2.1**: Form handling and comprehensive CSRF protection
- **Flask-Session**: Redis-backed session storage for scalability
- **APScheduler 3.10.4**: Background task scheduling and maintenance jobs

### Database & Storage
- **PostgreSQL**: Production database with full-text search capabilities
- **SQLite**: Development database with seamless migration path
- **Redis 5.0.1**: Session storage, caching, and real-time features
- **File Upload Security**: Secure handling with type validation and size limits

### AI & Machine Learning
- **Ollama Integration**: Local LLM serving for privacy-first AI features
- **Computer Vision**: PIL/Pillow for advanced image processing
- **Barcode Recognition**: pyzbar for product identification
- **Natural Language Processing**: Custom food parsing and nutrition extraction

### External APIs & Integrations  
- **Open Food Facts API**: Global nutrition database with 2M+ products
- **Wikipedia API**: Supplementary food information and nutritional data
- **RESTful Architecture**: Well-documented API with OpenAPI 3.0 specification

### Frontend & UI Technologies
- **Jinja2 Templates**: Server-side rendering with component-based structure
- **Bootstrap 5**: Responsive CSS framework with custom themes
- **JavaScript/AJAX**: Dynamic interactions and real-time updates
- **Server-Sent Events**: Streaming AI chat responses
- **Chart.js**: Interactive data visualization and progress tracking

### Mobile Development
- **Flutter**: Cross-platform mobile framework (Android, iOS, Web, Windows)
- **Dart**: Modern programming language with null safety
- **Material Design 3**: Native UI components and smooth animations
- **Camera Integration**: Photo capture with permission handling
- **HTTP Client**: Secure API communication with the Flask backend

### Testing & Quality Assurance
- **Pytest 7.4.3**: Comprehensive unit testing framework with fixtures
- **Playwright 1.40.0**: End-to-end browser automation and testing
- **Coverage Reports**: HTML coverage reporting with threshold enforcement
- **Code Quality**: Black formatting, isort imports, flake8 linting
- **Pre-commit Hooks**: Automated code quality enforcement

### DevOps & Deployment
- **Docker**: Production-ready containerization with health checks
- **Docker Compose**: Multi-container orchestration (app, database, Redis)
- **Environment Management**: Comprehensive .env configuration support
- **Health Monitoring**: Container health checks and graceful shutdowns
- **Makefile**: Streamlined development workflow commands

### Security Features
- **BCrypt Password Hashing**: Industry-standard password protection with salt rounds
- **CSRF Protection**: Comprehensive token-based protection on all forms
- **Session Security**: HTTPOnly cookies with secure Redis backing
- **Role-Based Access Control**: Admin functionality with proper authorization
- **Input Validation**: WTForms validation with custom security rules
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries

## 🛠 Development

### Project Structure

```
nutrition-ai/
├── app.py                    # Flask application factory with scheduler
├── config.py                # Environment-based configuration classes
├── extensions.py            # Flask extensions initialization
├── constants.py             # Application constants (NEW)
├── models.py                # SQLAlchemy database models (11 models)
├── forms/                   # WTForms form definitions by feature
├── routes/                  # Flask blueprints (6 main blueprints)
│   ├── auth.py             # Authentication with default prompts
│   ├── main.py             # Dashboard and core features
│   ├── onboarding.py       # 4-step user setup wizard
│   ├── settings.py         # User preferences and AI config
│   ├── coach.py            # AI chat with streaming responses
│   └── admin.py            # Administrative functionality
├── api/                     # RESTful API endpoints
├── services/                # Business logic and external integrations
├── templates/               # Jinja2 HTML templates with Bootstrap
├── static/                  # CSS, JS, images, uploads
├── scripts/                 # Utility scripts including admin tools
├── nutrition_ai_mobile/     # Flutter mobile companion app
├── tests/                   # Comprehensive testing suite
│   ├── unit/               # Unit tests for models and services
│   ├── e2e/                # End-to-end Playwright tests
│   └── integration/        # Integration tests
├── docs/                    # Extensive documentation and guides
├── docker-compose.yml       # Production Docker setup
├── Dockerfile              # Multi-stage container build
└── requirements.txt         # Python dependencies
```

### Key Components

#### Database Models (`models.py`) - 11 Core Models
- **User**: Authentication with admin flags and cascading relationships
- **Profile**: User preferences, goals, and lifestyle data stored as JSON fields
- **Settings**: AI configuration with default system prompts and Ollama settings
- **FoodLog**: Comprehensive nutrition logging with macro/micronutrient tracking
- **FoodItem**: Cached food database entries from external APIs with source tracking
- **CoachMessage**: AI chat history with role-based storage and source references
- **Photo**: Food image uploads with AI analysis results and metadata
- **WeighIn/WaterIntake**: Health tracking data with progress monitoring
- **SystemLog/GlobalSettings**: Admin and system management capabilities

#### Service Layer (`services/`) - Clean Architecture
- **OllamaClient**: Intelligent Ollama interface with Docker auto-correction and user-specific settings
- **NutritionSearch**: Open Food Facts API and Wikipedia integration with caching
- **FoodParser**: AI-powered food recognition from photos with confidence scoring
- **RecommendationService**: Personalized meal suggestions and calorie targets
- **AnalyticsService**: Progress tracking, trend analysis, and data visualization
- **VisionClassifier**: Advanced image processing for food recognition

#### RESTful API (`api/routes.py`) - Complete Coverage
- `/api/logs` - CRUD operations for food logging with filtering
- `/api/coach/chat` - Streaming AI chat responses via Server-Sent Events
- `/api/photo/upload` - Secure image upload and AI analysis pipeline
- `/api/analytics/*` - Progress data, charts, and trend analysis endpoints
- `/api/models/*` - Ollama model management and health checking
- `/api/export/*` - Data export capabilities (CSV, JSON)
- `/api/healthz` - Container health monitoring endpoint

### Running Tests

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run end-to-end tests with Playwright
make test-e2e

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Install pre-commit hooks
pre-commit install
```

### Database Migrations

```bash
# Initialize migrations (first time)
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## 🐳 Docker Deployment

### Production Deployment

```bash
# Build and start services
docker compose up -d

# View logs
docker compose logs -f app

# Stop services
docker compose down
```

### Development with Docker

Use the same command as above. Default access: http://localhost:5001

## 📊 API Documentation

- Swagger UI: http://localhost:5001/api/docs
- OpenAPI spec (YAML): http://localhost:5001/openapi.yaml

### Authentication

All API endpoints require authentication except `/api/healthz`.

### Core Endpoints

#### Food Logging
```bash
# Get food logs
GET /api/logs?date=2024-01-01&limit=50

# Create food log
POST /api/logs
{
  "custom_name": "Apple",
  "meal": "snack",
  "grams": 150,
  "calories": 80,
  "protein_g": 0.5,
  "carbs_g": 20,
  "fat_g": 0.2
}

# Delete food log
DELETE /api/logs/{id}
```

#### AI Coach
```bash
# Chat with AI (streaming)
POST /api/coach/chat
{
  "message": "What should I eat for breakfast?"
}
```

#### Photo Analysis
```bash
# Upload food photo
POST /api/photo/upload
Content-Type: multipart/form-data
photo: <image file>
```

#### Analytics
```bash
# Get nutrition trends
GET /api/analytics/nutrition-trends?days=30

# Get dashboard data
GET /api/analytics/dashboard

# Export data
GET /api/export/logs.csv?from=2024-01-01&to=2024-01-31
```

### Response Format

All API responses follow this structure:

```json
{
  "data": {...},
  "message": "Success message",
  "error": null
}
```

Error responses:

```json
{
  "error": "Error description",
  "code": 400
}
```

## 🧪 Testing

### Test Structure

- **Unit Tests**: Test individual components and services
- **Integration Tests**: Test API endpoints and database interactions
- **End-to-End Tests**: Full user journey testing with Playwright

### Running Specific Tests

```bash
# Test specific module
python -m pytest tests/unit/test_auth.py

# Test with specific marker
python -m pytest -m "unit"

# Test with coverage
python -m pytest --cov=services tests/unit/test_services.py
```

### End-to-End Testing

E2E tests use Playwright to simulate real user interactions:

```bash
# Install Playwright browsers
python -m playwright install

# Run E2E tests (requires running application)
python -m pytest tests/e2e/ --headed
```

## 🔐 Security

### Security Features

- **Password Hashing**: BCrypt with salt rounds
- **CSRF Protection**: All forms include CSRF tokens
- **File Upload Security**: Type validation and size limits
- **Session Management**: Secure session cookies
- **Input Validation**: Comprehensive form validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection

### Security Best Practices

1. **Environment Variables**: Never commit secrets to version control
2. **HTTPS**: Use HTTPS in production
3. **Regular Updates**: Keep dependencies updated
4. **Access Control**: Implement proper user authentication
5. **Data Privacy**: Local AI processing for sensitive data

## 🚀 Performance

### Optimization Features

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Redis integration for session storage
- **Image Optimization**: Automatic image resizing and compression
- **Lazy Loading**: Progressive data loading in UI
- **CDN Ready**: Static assets can be served from CDN

### Performance Monitoring

- **Health Check**: `/api/healthz` endpoint for monitoring
- **Request Logging**: Comprehensive application logging
- **Error Tracking**: Proper error handling and reporting

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `make test`
5. Ensure code quality: `make lint`
6. Commit changes: `git commit -am 'Add feature'`
7. Push branch: `git push origin feature-name`
8. Create Pull Request

### Code Style

- **Python**: Follow PEP 8, use Black formatter
- **HTML/CSS**: Follow semantic HTML practices
- **JavaScript**: Use modern ES6+ syntax
- **Documentation**: Update README and docstrings

### Testing Requirements

- Unit tests for new functions
- Integration tests for API endpoints
- E2E tests for new user flows
- Maintain test coverage above 80%

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Flask**: Web framework
- **Ollama**: Local AI model serving
- **Open Food Facts**: Nutrition database
- **Tailwind CSS**: UI styling
- **HTMX**: Dynamic interactions
- **Playwright**: End-to-end testing
- **Chart.js**: Data visualization

## 📞 Support

- **Issues**: Report bugs and feature requests on GitHub Issues
- **Documentation**: Check the [Wiki](../../wiki) for detailed guides
- **Community**: Join discussions in [Discussions](../../discussions)

## 🗺 Roadmap

### Upcoming Features
- [ ] Advanced offline mode for mobile app
- [ ] Meal planning and grocery lists
- [ ] Nutrition goal templates and challenges
- [ ] Recipe import, scaling, and meal prep
- [ ] Social features and progress sharing
- [ ] Enhanced ML models for food recognition
- [ ] Integration with fitness trackers and wearables
- [ ] Nutritionist collaboration and consultation features
- [ ] Voice-to-text food logging
- [ ] Batch photo processing for meal prep

### Recent Updates & Version History

#### **v1.2.0**: Enhanced AI & Mobile Features
- ✅ **Default System Prompts**: Automatic coaching prompt assignment for all users
- ✅ **Flutter Mobile App**: Complete cross-platform mobile companion
- ✅ **Photo Food Analysis**: Camera integration with AI-powered recognition
- ✅ **Enhanced Security**: Comprehensive CSRF protection and admin controls
- ✅ **Streaming Chat**: Real-time AI responses with Server-Sent Events
- ✅ **Docker Optimization**: Production-ready containerization with health monitoring

#### **v1.0.0**: Initial Release
- ✅ User authentication and 4-step onboarding
- ✅ Multi-modal food logging (manual, photo, barcode)
- ✅ AI coach integration with Ollama
- ✅ Progress tracking and analytics dashboard
- ✅ Admin functionality with user management
- ✅ RESTful API with interactive documentation

---

**Built with ❤️ for better nutrition tracking and privacy-first AI**

## 📱 Mobile App (Flutter)

### Cross-Platform Mobile Companion
The Flutter mobile app provides a native mobile experience across all platforms:

```bash
cd nutrition_ai_mobile
flutter pub get
flutter run -d android    # Android development
flutter run -d ios        # iOS development  
flutter run -d chrome     # Web deployment
flutter run -d windows    # Windows desktop
```

### Mobile App Features
- **🏠 Dashboard**: Nutrition overview with quick action buttons
- **📷 Photo Logging**: Camera integration with AI food recognition
- **🔍 Food Search**: Real-time search of nutrition database
- **📝 Manual Entry**: Complete food logging with nutrition details
- **⚙️ Server Setup**: Flexible backend configuration for any deployment
- **🎨 Material Design 3**: Modern UI with confidence indicators and animations

### Mobile Configuration
Configure the API endpoint based on your deployment:
- **Development**: `http://localhost:5001`
- **Android Emulator**: `http://10.0.2.2:5001`
- **Physical Device**: `http://YOUR-LAN-IP:5001` (e.g., `http://192.168.1.20:5001`)
- **Production**: `https://your-domain.com`

### Mobile Development Setup
```bash
# Install Flutter dependencies
flutter doctor                    # Verify Flutter installation
flutter pub get                  # Install package dependencies
flutter pub upgrade              # Update to latest packages

# Platform-specific setup
flutter config --enable-web      # Enable web development
flutter config --enable-windows  # Enable Windows desktop
flutter config --enable-macos    # Enable macOS desktop
flutter config --enable-linux    # Enable Linux desktop
```

For complete mobile app documentation, see `docs/mobile_app.md`.