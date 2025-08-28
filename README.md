# NutriCoach 🥗🤖

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

**NutriCoach** is a complete, production-ready AI-powered nutrition tracking web application built with Flask. It combines intelligent food recognition, personalized AI coaching, and comprehensive nutrition analytics to help users achieve their health goals.

## ✨ Features

### 🤖 **AI-Powered Intelligence**
- **AI Nutrition Coach**: Get personalized advice powered by Ollama LLMs
- **Photo Food Recognition**: Upload food photos for automatic identification and nutrition analysis
- **Smart Meal Suggestions**: Context-aware food recommendations based on your goals and preferences

### 📊 **Comprehensive Tracking**
- **Multi-Modal Food Logging**: Manual entry, photo upload, or barcode scanning
- **Progress Analytics**: Detailed charts and insights into your nutrition trends
- **Goal-Based Targets**: Personalized calorie and macro targets based on your profile

### 🔒 **Privacy-First Design**
- **Local AI Processing**: Use your own Ollama instance for complete data privacy
- **Secure Authentication**: BCrypt password hashing and CSRF protection
- **Offline Capability**: Works without external API calls when needed

### 🎨 **Modern User Experience**
- **Responsive Design**: Mobile-first design that works on all devices
- **Dark Mode**: Built-in dark/light theme switching
- **Real-time Updates**: HTMX-powered dynamic interface
- **Accessibility**: WCAG AA compliant with proper ARIA labels

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

## 🛠 Development

### Project Structure

```
nutrition-ai/
├── app.py                 # Flask application factory
├── config.py             # Configuration classes
├── extensions.py         # Flask extensions initialization
├── models.py             # SQLAlchemy database models
├── forms/                # WTForms form definitions
├── routes/               # Flask blueprints and routes
├── api/                  # API endpoints
├── services/             # Business logic and external integrations
├── templates/            # Jinja2 HTML templates
├── static/               # CSS, JS, images, uploads
├── tests/                # Unit and integration tests
│   ├── unit/            # Unit tests
│   └── e2e/             # End-to-end Playwright tests
├── docker-compose.yml    # Docker setup
├── Dockerfile           # Container definition
└── requirements.txt      # Python dependencies
```

### Key Components

#### Models (`models.py`)
- **User**: Authentication and user management
- **Profile**: User preferences, goals, and lifestyle data
- **Settings**: AI and application configuration
- **FoodLog**: Nutrition logging entries
- **FoodItem**: Food database cache
- **CoachMessage**: AI chat history
- **WeighIn/WaterIntake**: Health tracking data

#### Services (`services/`)
- **OllamaClient**: Interface to Ollama AI models
- **NutritionSearch**: Open Food Facts and Wikipedia integration
- **FoodParser**: Food recognition and nutrition parsing
- **RecommendationService**: Personalized suggestions and targets
- **AnalyticsService**: Progress tracking and data analysis

#### API Endpoints (`api/routes.py`)
- `/api/logs` - Food logging CRUD operations
- `/api/coach/chat` - AI chat streaming
- `/api/photo/upload` - Image upload and analysis
- `/api/analytics/*` - Progress data and charts
- `/api/models/*` - Ollama model management

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
- [ ] Meal planning and grocery lists
- [ ] Nutrition goal templates
- [ ] Recipe import and scaling
- [ ] Social features and sharing
- [ ] Mobile app (React Native)
- [ ] Advanced ML models for food recognition
- [ ] Integration with fitness trackers
- [ ] Nutritionist collaboration features

### Version History

- **v1.0.0**: Initial release with core features
  - User authentication and onboarding
  - Food logging (manual, photo, barcode)
  - AI coach integration
  - Progress tracking and analytics
  - Docker deployment ready

---

**Built with ❤️ for better nutrition tracking**

## 📱 Mobile App (Flutter)

A companion Flutter app is available in `nutrition_ai_mobile/`.

- Documentation: `docs/mobile_app.md`
- Quick start:
  ```bash
  cd nutrition_ai_mobile
  flutter pub get
  flutter run -d android   # or ios / chrome / windows
  ```
- Configure the server URL in the app (e.g., `http://localhost:5001` or `http://10.0.2.2:5001` for Android emulator).