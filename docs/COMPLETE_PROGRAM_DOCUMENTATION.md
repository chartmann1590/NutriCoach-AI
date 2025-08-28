# NutriCoach - Complete Program Documentation

**AI-Powered Nutrition Tracking & Coaching Platform**

*Generated: August 22, 2025*  
*Version: 1.0*  
*Status: ✅ Complete Documentation with Screenshots*

---

## Table of Contents

1. [Application Overview](#application-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Core Features](#core-features)
4. [User Journey & Workflows](#user-journey--workflows)
5. [Admin Panel](#admin-panel)
6. [API Documentation](#api-documentation)
7. [Database Schema](#database-schema)
8. [Services & Integration](#services--integration)
9. [Screenshots Gallery](#screenshots-gallery)
10. [Technical Implementation](#technical-implementation)
11. [Security & Privacy](#security--privacy)
12. [Installation & Setup](#installation--setup)

---

## Application Overview

### What is NutriCoach?

NutriCoach is a comprehensive, privacy-focused nutrition tracking and AI coaching platform that combines modern web technologies with local AI processing to provide personalized nutrition guidance. The application offers intelligent food logging through multiple methods, detailed analytics, and an AI-powered coaching system.

### Key Value Propositions

- **Privacy-First Design**: All AI processing happens locally using Ollama, ensuring user data never leaves their device
- **Multi-Modal Food Logging**: Photo recognition, barcode scanning, manual entry, and text search
- **Intelligent Recommendations**: Personalized meal suggestions based on goals, preferences, and dietary restrictions
- **Comprehensive Analytics**: Detailed progress tracking with visual charts and insights
- **Professional-Grade Features**: Admin panel, user management, and system monitoring capabilities

### Target Users

- **Individual Users**: People seeking intelligent nutrition tracking and coaching
- **Healthcare Professionals**: Nutritionists and dietitians managing client data
- **Fitness Enthusiasts**: Athletes and fitness-focused individuals tracking performance nutrition
- **Organizations**: Companies implementing wellness programs

---

## Architecture & Technology Stack

### Frontend Technologies
- **HTML5/CSS3**: Modern responsive design with Tailwind CSS
- **JavaScript**: Vanilla JS with Chart.js for analytics visualization
- **Jinja2 Templates**: Server-side rendering for optimal performance

### Backend Technologies
- **Flask**: Python web framework with Blueprint architecture
- **SQLAlchemy**: Database ORM with migration support via Alembic
- **Flask-Login**: User session management and authentication
- **Flask-WTF**: Form handling with CSRF protection

### Database
- **SQLite**: Default database for development and small deployments
- **PostgreSQL**: Recommended for production environments
- **Database Models**: 11 comprehensive models covering all application needs

### AI & Machine Learning
- **Ollama**: Local AI model serving for privacy-focused AI features
- **Computer Vision**: Food recognition from photos
- **Natural Language Processing**: Chat-based nutrition coaching

### External Integrations
- **Open Food Facts API**: Nutrition database for packaged foods
- **Wikipedia API**: General food information lookup
- **Barcode Scanning**: Product identification and nutrition retrieval

### Infrastructure
- **Docker**: Containerized deployment with multi-stage builds
- **Background Jobs**: APScheduler for maintenance tasks
- **File Storage**: Local file system with organized structure

---

## Core Features

### 1. Multi-Modal Food Logging

#### Photo Food Recognition
- **AI-Powered Analysis**: Upload food photos for automatic identification
- **Portion Estimation**: Visual portion size estimation from images
- **Nutrition Calculation**: Automatic nutritional breakdown from visual analysis
- **Fallback Systems**: Robust fallback when AI services are unavailable

*Screenshot: Photo Upload Interface*
![Photo Upload](screenshots/registration/reg_13_photo_upload.png)

#### Barcode Scanning
- **Instant Recognition**: Scan product barcodes for immediate nutrition data
- **Database Integration**: Links to Open Food Facts comprehensive database
- **Brand Recognition**: Identifies specific product brands and variants

#### Manual Entry
- **Comprehensive Search**: Search across multiple nutrition databases
- **Custom Foods**: Add personal recipes and custom food items
- **Portion Control**: Flexible portion size entry with unit conversions

*Screenshot: Food Logging Interface*
![Food Logging](screenshots/registration/reg_12_food_logging.png)

#### Text Search
- **Multi-Source Search**: Searches Open Food Facts, Wikipedia, and local database
- **Intelligent Matching**: Smart food name matching and suggestions
- **Nutrition Estimation**: Fallback estimation for unknown foods

### 2. AI Nutrition Coaching

#### Personalized Chat Interface
- **Local AI Processing**: Privacy-focused coaching using Ollama models
- **Context-Aware Responses**: Understands user goals, preferences, and current nutrition status
- **Real-Time Streaming**: Live response generation for natural conversation flow
- **Conversation History**: Maintains chat history for context continuity

*Screenshot: AI Coach Interface*
![AI Coach](screenshots/registration/reg_14_ai_coach.png)

#### Intelligent Recommendations
- **Goal-Based Suggestions**: Recommendations aligned with weight loss/gain/maintenance goals
- **Dietary Restriction Support**: Respects allergies, preferences, and dietary requirements
- **Activity Level Integration**: Adjusts recommendations based on user activity levels
- **Contextual Timing**: Time-appropriate meal suggestions

#### Safety Features
- **Medical Disclaimer Integration**: Clear boundaries on medical advice
- **Evidence-Based Guidance**: Recommendations based on nutrition science
- **Safety Mode**: Optional conservative mode for sensitive users

### 3. Comprehensive Analytics

#### Progress Tracking
- **Weight Trends**: Visual weight progression with trend analysis
- **Nutrition Trends**: Calorie and macronutrient tracking over time
- **Goal Progress**: Visual progress toward weight and nutrition targets
- **Streak Tracking**: Gamification through consistent logging rewards

*Screenshot: Progress Analytics*
![Progress Analytics](screenshots/registration/reg_15_progress_fixed_temp.png)

#### Data Visualization
- **Interactive Charts**: Chart.js-powered visualizations
- **Macro Distribution**: Pie charts showing protein/carbs/fat ratios
- **Meal Distribution**: Analysis of calorie distribution across meals
- **Weekly/Monthly Views**: Multiple time period analysis options

#### Export Capabilities
- **CSV Export**: Download nutrition data for external analysis
- **Date Range Selection**: Custom time period exports
- **Complete Data Access**: All user data available for download

### 4. Personalized Goal Setting

#### Scientific Calculations
- **BMR/TDEE Calculation**: Mifflin-St Jeor equation for accurate metabolic rate
- **Activity Level Integration**: Adjusts calorie needs based on activity level
- **Goal-Specific Targets**: Different calculations for weight loss, maintenance, and gain
- **Macro Target Setting**: Personalized protein, carbohydrate, and fat targets

#### Lifestyle Integration
- **Dietary Preferences**: Supports vegetarian, vegan, keto, paleo, and other diets
- **Allergy Management**: Filters foods based on allergies and intolerances
- **Budget Considerations**: Meal suggestions within specified budget ranges
- **Cooking Skill Adaptation**: Recipes matched to user cooking abilities

### 5. User Profile Management

#### Comprehensive Onboarding
- **4-Step Process**: Progressive profile building for optimal personalization
- **Skip Options**: Flexible onboarding with default value fallbacks
- **Progress Tracking**: Session-based progress through onboarding steps

*Screenshot: Onboarding Step 1*
![Onboarding Step 1](screenshots/registration/reg_04_onboarding_step1.png)

*Screenshot: Onboarding Step 2*
![Onboarding Step 2](screenshots/registration/reg_06_onboarding_step2.png)

#### Settings Management
- **Profile Updates**: Easy modification of personal information and goals
- **AI Configuration**: User-controlled AI model selection and settings
- **Privacy Controls**: Granular control over data sharing and processing
- **Data Export**: Complete data portability for users

*Screenshot: Settings Interface*
![Settings](screenshots/registration/reg_16_settings.png)

---

## User Journey & Workflows

### New User Registration

#### 1. Homepage Introduction
Users are welcomed with a comprehensive overview of NutriCoach features and benefits.

*Screenshot: Homepage*
![Homepage](screenshots/registration/reg_01_homepage.png)

#### 2. Simple Registration
Minimal friction registration requiring only username and password.

*Screenshot: Registration Form*
![Registration Form](screenshots/registration/reg_02_registration_form.png)

*Screenshot: Registration Filled*
![Registration Filled](screenshots/registration/reg_03_form_filled.png)

#### 3. Comprehensive Onboarding

**Step 1: Basic Information**
- Name, age, sex, height, and current weight
- Foundation for accurate nutrition calculations

*Screenshot: Onboarding Step 1 Filled*
![Step 1 Filled](screenshots/registration/reg_05_step1_filled.png)

**Step 2: Goals & Activity**
- Activity level selection (sedentary to very active)
- Goal type (lose weight, maintain, gain weight)
- Target weight and realistic timeframe

*Screenshot: Onboarding Step 2 Filled*
![Step 2 Filled](screenshots/registration/reg_07_step2_filled.png)

**Step 3: Lifestyle & Preferences**
- Dietary preferences and restrictions
- Cooking skills and available equipment
- Budget range and meal frequency preferences

*Screenshot: Onboarding Step 3*
![Step 3](screenshots/registration/reg_08_onboarding_step3.png)

*Screenshot: Onboarding Step 3 Filled*
![Step 3 Filled](screenshots/registration/reg_09_step3_filled.png)

**Step 4: AI Configuration**
- Ollama URL configuration for local AI processing
- Model selection and connection testing
- Privacy and safety settings

*Screenshot: Onboarding Step 4*
![Step 4](screenshots/registration/reg_10_onboarding_step4.png)

#### 4. Dashboard Access
After completing onboarding, users access their personalized dashboard with calculated nutrition targets.

*Screenshot: Complete Dashboard*
![Complete Dashboard](screenshots/registration/reg_11_dashboard_complete.png)

### Daily Usage Workflow

#### Morning Routine
1. **Dashboard Check**: Review yesterday's progress and today's targets
2. **Breakfast Logging**: Use photo, barcode, or manual entry
3. **AI Consultation**: Ask coach for meal suggestions or questions

#### Throughout the Day
1. **Meal Logging**: Real-time food tracking with multiple input methods
2. **Progress Monitoring**: Check remaining calories and macro targets
3. **Quick Logging**: Water intake and weight measurements

#### Evening Review
1. **Progress Analysis**: Review daily nutrition completion
2. **Trend Analysis**: Check weekly and monthly progress
3. **Planning**: Get suggestions for tomorrow's meals

### Data Export Workflow
1. **Settings Access**: Navigate to export settings
2. **Date Range Selection**: Choose specific time period
3. **CSV Download**: Receive complete nutrition data
4. **External Analysis**: Import data into preferred analytics tools

---

## Admin Panel

### System Administration Features

#### User Management
- **User Overview**: Complete list of registered users with search and filtering
- **User Creation**: Admin-controlled user account creation
- **User Editing**: Modify user profiles, goals, and settings
- **Bulk Operations**: Bulk user actions for efficient management

*Screenshot: Admin Dashboard*
![Admin Dashboard](screenshots/admin/admin_04_dashboard.png)

*Screenshot: User Management*
![User Management](screenshots/admin/admin_05_user_management.png)

#### System Configuration
- **Global Settings**: System-wide configuration management
- **Ollama Configuration**: Central AI model management
- **Security Settings**: System security and access controls

*Screenshot: Ollama Settings*
![Admin Ollama Settings](screenshots/admin/admin_06_ollama_settings.png)

#### Monitoring & Maintenance
- **System Logs**: Comprehensive audit trail and error logging
- **Performance Monitoring**: System health and performance metrics
- **Maintenance Tools**: Database cleanup and optimization utilities

*Screenshot: System Logs*
![System Logs](screenshots/admin/admin_07_system_logs.png)

*Screenshot: Maintenance Tools*
![Maintenance](screenshots/admin/admin_08_maintenance.png)

#### Security Features
- **Role-Based Access**: Admin vs. user privilege separation
- **Login Protection**: Admin route protection and authentication
- **Audit Logging**: Complete tracking of administrative actions

*Screenshot: Admin Login Protection*
![Admin Login Protection](screenshots/admin/admin_02_login_protection.png)

---

## API Documentation

### RESTful API Endpoints

#### Authentication Required Endpoints

**Health Check**
```
GET /api/healthz
Response: {"status": "healthy", "timestamp": "2025-08-22T..."}
```

**Nutrition Search**
```
GET /api/search_nutrition?q={query}
Response: {"query": "apple", "results": [...], "count": 5}
```

**Barcode Search**
```
GET /api/search_barcode?barcode={barcode}
Response: {"result": {"name": "...", "nutrition": {...}}}
```

**Food Logging**
```
POST /api/logs
Body: {
  "custom_name": "Apple",
  "meal": "snack",
  "grams": 150,
  "calories": 78,
  "protein_g": 0.3,
  "carbs_g": 21,
  "fat_g": 0.2
}
Response: {"id": 123, "message": "Food logged successfully"}
```

**Get Food Logs**
```
GET /api/logs?date=2025-08-22&limit=50
Response: {"logs": [...], "count": 10}
```

**Photo Upload & Analysis**
```
POST /api/photo/upload
Body: FormData with 'photo' field
Response: {
  "photo_id": 456,
  "filename": "food_image.jpg",
  "candidates": [
    {"name": "apple", "confidence": 0.95, "nutrition": {...}}
  ]
}
```

**AI Coach Chat**
```
POST /api/coach/chat
Body: {"message": "What should I eat for breakfast?"}
Response: Server-Sent Events stream with AI responses
```

**Weight & Water Tracking**
```
POST /api/weigh-in
Body: {"weight_kg": 70.5}

POST /api/water-intake  
Body: {"ml": 250}
```

#### Analytics Endpoints

**Nutrition Trends**
```
GET /api/analytics/nutrition-trends?days=30
Response: {
  "dates": ["2025-08-01", ...],
  "calories": [2000, 1950, ...],
  "protein": [150, 145, ...],
  "carbs": [250, 240, ...],
  "fat": [67, 65, ...]
}
```

**Weight Trends**
```
GET /api/analytics/weight-trends?days=90
Response: {
  "dates": [...],
  "weights": [...],
  "trend": [...]
}
```

**Dashboard Data**
```
GET /api/analytics/dashboard
Response: {
  "today": {...},
  "weekly": {...},
  "meal_distribution": {...},
  "macro_distribution": {...},
  "streaks": {...},
  "top_foods": [...]
}
```

**Data Export**
```
GET /api/export/logs.csv?from=2025-08-01&to=2025-08-22
Response: CSV file download
```

#### Model Management Endpoints

**List Ollama Models**
```
GET /api/models/list
Response: {"models": ["llama2", "llava"], "count": 2}
```

**Pull Model**
```
POST /api/models/pull
Body: {"model": "llama2"}
Response: {"status": "success", "message": "Model pulled successfully"}
```

**Test Connection**
```
POST /api/settings/test_ollama
Body: {"ollama_url": "http://localhost:11434"}
Response: {"connected": true, "url": "..."}
```

---

## Database Schema

### Core Models

#### User Model
```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
```

#### Profile Model
```python
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    height_cm = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    
    # Goals
    activity_level = db.Column(db.String(20), nullable=False)
    goal_type = db.Column(db.String(20), nullable=False)
    target_weight_kg = db.Column(db.Float)
    timeframe_weeks = db.Column(db.Integer)
    
    # Preferences (JSON)
    preferences = db.Column(db.Text)  # Dietary preferences
    allergies = db.Column(db.Text)    # Allergies list
    conditions = db.Column(db.Text)   # Medical conditions
    
    # Lifestyle
    budget_range = db.Column(db.String(20))
    cooking_skill = db.Column(db.String(20))
    equipment = db.Column(db.Text)    # Kitchen equipment
    meals_per_day = db.Column(db.Integer, default=3)
    sleep_schedule = db.Column(db.String(50))
```

#### FoodLog Model
```python
class FoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    food_item_id = db.Column(db.Integer, db.ForeignKey('food_item.id'))
    
    # Food Details
    custom_name = db.Column(db.String(200))
    meal = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack
    grams = db.Column(db.Float, nullable=False)
    
    # Nutritional Data
    calories = db.Column(db.Float, nullable=False)
    protein_g = db.Column(db.Float, default=0)
    carbs_g = db.Column(db.Float, default=0)
    fat_g = db.Column(db.Float, default=0)
    fiber_g = db.Column(db.Float, default=0)
    sugar_g = db.Column(db.Float, default=0)
    sodium_mg = db.Column(db.Float, default=0)
    micros = db.Column(db.Text)  # JSON micronutrients
    
    # Metadata
    source = db.Column(db.String(20), nullable=False)  # manual, vision, barcode
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Supporting Models

#### Settings Model
```python
class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Ollama Configuration
    ollama_url = db.Column(db.String(255), default='http://localhost:11434')
    chat_model = db.Column(db.String(100))
    vision_model = db.Column(db.String(100))
    system_prompt = db.Column(db.Text)
    
    # AI Behavior
    safety_mode = db.Column(db.Boolean, default=True)
```

#### CoachMessage Model
```python
class CoachMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role = db.Column(db.String(20), nullable=False)  # system, user, assistant
    content = db.Column(db.Text, nullable=False)
    refs = db.Column(db.Text)  # JSON references
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### Photo Model
```python
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filepath = db.Column(db.String(255), nullable=False)
    analysis = db.Column(db.Text)  # JSON analysis results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Administrative Models

#### SystemLog Model
```python
class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False)  # info, warning, error, critical
    action = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    extra_data = db.Column(db.Text)  # JSON additional data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### GlobalSettings Model
```python
class GlobalSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='general')
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## Services & Integration

### Analytics Service
**Purpose**: Advanced analytics and reporting engine

**Key Capabilities**:
- Nutrition trend analysis with moving averages
- Weight progression tracking with trend lines
- Meal distribution analysis across time periods
- Macro distribution calculations and visualization
- Logging streak gamification
- Comprehensive data export functionality

**Integration Points**: FoodLog, WeighIn, WaterIntake, Profile models

### Recommendation Service
**Purpose**: Intelligent recommendation engine using nutrition science

**Key Capabilities**:
- BMR/TDEE calculation using Mifflin-St Jeor equation
- Personalized daily calorie and macro targets
- Context-aware meal suggestions
- Progress insights and recommendations
- Goal-specific nutrition adjustments

**Integration Points**: Profile, FoodLog, and AI coaching system

### Nutrition Search Service
**Purpose**: Multi-source food database integration

**Key Capabilities**:
- Open Food Facts API integration for packaged foods
- Wikipedia API for general food information
- Barcode scanning and product recognition
- Built-in nutrition database for offline functionality
- Intelligent fallback systems for data reliability

**External APIs**: Open Food Facts, Wikipedia

### Ollama Client Service
**Purpose**: Local AI integration for privacy-focused features

**Key Capabilities**:
- Connection management and health monitoring
- Model management (list, pull, update)
- Chat functionality with streaming responses
- Vision analysis for food photo recognition
- Configurable safety and system prompts

**External Integration**: Ollama AI server (local)

### Vision Classifier Service
**Purpose**: Computer vision for food identification

**Key Capabilities**:
- Food identification using Food-101 dataset
- Portion size estimation from visual cues
- Fallback classification when AI unavailable
- Integration with Ollama vision models

**Fallback Systems**: Mock classification for development

### Food Parser Service
**Purpose**: Data processing and integration layer

**Key Capabilities**:
- Vision result processing and structuring
- Barcode data parsing and validation
- Natural language portion parsing
- Multi-source data fusion with priority systems
- Nutrition data validation and sanitization

**Integration Points**: All food-related services and APIs

---

## Security & Privacy

### Privacy-First Architecture

#### Local AI Processing
- **Ollama Integration**: All AI processing happens locally on user's device
- **No Cloud Dependencies**: User data never transmitted to external AI services
- **User-Controlled Models**: Users choose and manage their own AI models

#### Data Protection
- **Password Security**: Bcrypt hashing with salt for password storage
- **Session Management**: Secure session handling with Flask-Login
- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **Input Validation**: Comprehensive server-side validation

#### User Rights
- **Data Portability**: Complete data export in CSV format
- **Data Deletion**: User account and data deletion capabilities
- **Privacy Controls**: Granular control over data sharing and processing
- **Audit Trail**: System logs for administrative actions

### Security Features

#### Authentication & Authorization
- **Role-Based Access Control**: Admin vs. user privilege separation
- **Protected Routes**: Login required decorators on sensitive endpoints
- **Admin Route Protection**: Additional admin privilege checks
- **Session Security**: Automatic logout and session protection

#### Input Security
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
- **XSS Protection**: Template escaping and input sanitization
- **File Upload Security**: Image processing and EXIF stripping
- **Size Limits**: File upload size restrictions

#### Administrative Security
- **Admin Account Protection**: Separate admin account creation process
- **Audit Logging**: Complete tracking of administrative actions
- **System Monitoring**: Health checks and error monitoring
- **Maintenance Tools**: Secure database operations

---

## Installation & Setup

### System Requirements

#### Minimum Requirements
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended for AI features)
- **Storage**: 2GB free space (additional space for AI models)
- **OS**: Windows, macOS, or Linux

#### Recommended Requirements
- **Python**: 3.10+
- **Memory**: 16GB RAM for optimal AI performance
- **Storage**: 10GB+ for full AI model collection
- **GPU**: NVIDIA GPU for accelerated AI processing (optional)

### Installation Methods

#### Option 1: Docker Deployment (Recommended)
```bash
# Clone repository
git clone https://github.com/your-org/nutricoach.git
cd nutricoach

# Build and run with Docker Compose
docker-compose up -d

# Access application at http://localhost:5001
```

#### Option 2: Local Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/nutricoach.git
cd nutricoach

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\\Scripts\\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db upgrade

# Run application
python app.py
```

#### Option 3: Production Deployment
```bash
# Use production requirements
pip install -r requirements_core.txt

# Set environment variables
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@localhost/nutricoach

# Initialize database
flask db upgrade

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Configuration

#### Environment Variables
```bash
# Application Configuration
FLASK_ENV=development|production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///nutricoach.db

# AI Configuration
OLLAMA_URL=http://localhost:11434
DEFAULT_CHAT_MODEL=llama2
DEFAULT_VISION_MODEL=llava

# File Upload Configuration
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# External API Configuration
OPENFOODFACTS_API_URL=https://world.openfoodfacts.org/api/v0
WIKIPEDIA_API_URL=https://en.wikipedia.org/api/rest_v1
```

#### Database Setup
```bash
# Create database (PostgreSQL example)
createdb nutricoach

# Run migrations
flask db upgrade

# Create admin user (optional)
python create_admin.py
```

#### Ollama Setup (Optional but Recommended)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull recommended models
ollama pull llama2          # Chat model
ollama pull llava           # Vision model
ollama pull codellama       # Code assistance

# Start Ollama service
ollama serve
```

### First-Time Setup

#### 1. Access Application
Navigate to `http://localhost:5001` in your web browser

#### 2. Create User Account
- Click "Get Started" on homepage
- Fill out registration form
- Complete 4-step onboarding process

#### 3. Configure AI Features (Optional)
- Navigate to Settings > Ollama Configuration
- Test connection to local Ollama instance
- Select preferred chat and vision models

#### 4. Start Tracking
- Begin logging food through various methods
- Explore AI coaching features
- Review progress analytics

### Troubleshooting

#### Common Issues

**Database Connection Errors**
```bash
# Check database URL
echo $DATABASE_URL

# Recreate database
flask db stamp head
flask db migrate
flask db upgrade
```

**Ollama Connection Issues**
```bash
# Check Ollama status
ollama list

# Restart Ollama service
pkill ollama
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

**Permission Errors**
```bash
# Fix file permissions
chmod -R 755 static/uploads/
chown -R www-data:www-data static/uploads/  # Linux production
```

**Memory Issues with AI**
- Reduce Ollama model size
- Increase system RAM
- Use lighter models (e.g., tinyllama)

#### Logs and Debugging
```bash
# Application logs
tail -f logs/app.log

# Database logs
tail -f logs/db.log

# Ollama logs
tail -f ~/.ollama/logs/server.log
```

---

## Screenshots Gallery

### Public Pages
- **Homepage**: [reg_01_homepage.png](screenshots/registration/reg_01_homepage.png)
- **Registration**: [reg_02_registration_form.png](screenshots/registration/reg_02_registration_form.png)

### Onboarding Process
- **Step 1 - Basic Info**: [reg_04_onboarding_step1.png](screenshots/registration/reg_04_onboarding_step1.png)
- **Step 2 - Goals**: [reg_06_onboarding_step2.png](screenshots/registration/reg_06_onboarding_step2.png)
- **Step 3 - Lifestyle**: [reg_08_onboarding_step3.png](screenshots/registration/reg_08_onboarding_step3.png)
- **Step 4 - AI Setup**: [reg_10_onboarding_step4.png](screenshots/registration/reg_10_onboarding_step4.png)

### Main Application
- **Dashboard**: [reg_11_dashboard_complete.png](screenshots/registration/reg_11_dashboard_complete.png)
- **Food Logging**: [reg_12_food_logging.png](screenshots/registration/reg_12_food_logging.png)
- **Photo Upload**: [reg_13_photo_upload.png](screenshots/registration/reg_13_photo_upload.png)
- **AI Coach**: [reg_14_ai_coach.png](screenshots/registration/reg_14_ai_coach.png)
- **Progress Analytics**: [reg_15_progress_fixed_temp.png](screenshots/registration/reg_15_progress_fixed_temp.png)
- **Settings**: [reg_16_settings.png](screenshots/registration/reg_16_settings.png)

### Admin Panel
- **Admin Dashboard**: [admin_04_dashboard.png](screenshots/admin/admin_04_dashboard.png)
- **User Management**: [admin_05_user_management.png](screenshots/admin/admin_05_user_management.png)
- **Ollama Settings**: [admin_06_ollama_settings.png](screenshots/admin/admin_06_ollama_settings.png)
- **System Logs**: [admin_07_system_logs.png](screenshots/admin/admin_07_system_logs.png)
- **Maintenance**: [admin_08_maintenance.png](screenshots/admin/admin_08_maintenance.png)

---

## Technical Implementation

### Code Organization

#### Blueprint Structure
```
app.py                    # Main application factory
├── routes/              # Route blueprints
│   ├── auth.py         # Authentication routes
│   ├── main.py         # Main application routes
│   ├── onboarding.py   # Onboarding flow
│   ├── settings.py     # Settings management
│   ├── coach.py        # AI coach routes
│   └── admin.py        # Admin panel routes
├── api/                # RESTful API
│   └── routes.py       # API endpoints
├── models.py           # Database models
├── services/           # Business logic
│   ├── analytics.py    # Analytics engine
│   ├── recommendations.py  # Recommendation engine
│   ├── nutrition_search.py # Food search
│   ├── ollama_client.py    # AI integration
│   ├── vision_classifier.py # Computer vision
│   └── food_parser.py      # Data processing
├── forms/              # WTForms
│   ├── auth.py         # Authentication forms
│   ├── onboarding.py   # Onboarding forms
│   ├── settings.py     # Settings forms
│   └── admin.py        # Admin forms
└── templates/          # Jinja2 templates
    ├── base.html       # Base template
    ├── auth/           # Authentication templates
    ├── onboarding/     # Onboarding templates
    ├── settings/       # Settings templates
    └── admin/          # Admin templates
```

#### Database Migrations
```bash
# Create migration
flask db migrate -m "Add new feature"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

#### Background Jobs
```python
from extensions import scheduler

@scheduler.task('interval', id='cleanup_job', hours=24)
def cleanup_old_data():
    """Daily cleanup of old data"""
    # Implementation
```

### Performance Optimization

#### Database Optimization
- **Indexes**: Strategic indexes on frequently queried columns
- **Query Optimization**: Efficient SQLAlchemy queries with proper joins
- **Connection Pooling**: Database connection pooling for concurrent users

#### Caching Strategies
- **Template Caching**: Jinja2 template compilation caching
- **Static File Caching**: Browser caching for CSS/JS assets
- **API Response Caching**: Short-term caching for expensive API calls

#### File Handling
- **Image Processing**: Automatic image resizing and optimization
- **EXIF Stripping**: Privacy protection through metadata removal
- **File Validation**: Comprehensive file type and size validation

### Testing Strategy

#### Unit Tests
```bash
# Run unit tests
pytest tests/unit/

# Test specific module
pytest tests/unit/test_services.py

# Test with coverage
pytest --cov=app tests/
```

#### Integration Tests
```bash
# Run integration tests
pytest tests/e2e/

# Test complete user journey
pytest tests/e2e/test_user_journey.py
```

#### End-to-End Tests
```bash
# Run Playwright tests
pytest tests/e2e/test_complete_application.py
```

---

## Conclusion

NutriCoach represents a comprehensive, privacy-focused nutrition tracking and AI coaching platform that successfully combines modern web technologies with local AI processing. The application provides users with intelligent food logging capabilities, personalized nutrition guidance, and detailed progress analytics while maintaining complete data privacy through local AI processing.

### Key Achievements

✅ **Complete Feature Set**: Multi-modal food logging, AI coaching, comprehensive analytics  
✅ **Privacy-First Design**: Local AI processing with Ollama integration  
✅ **Professional Admin Panel**: Full system administration capabilities  
✅ **Comprehensive API**: RESTful API for all application features  
✅ **Robust Architecture**: Scalable Flask application with Blueprint organization  
✅ **Complete Documentation**: Comprehensive documentation with screenshots  
✅ **Production Ready**: Docker deployment with security best practices  

### Future Enhancements

- **Mobile Application**: React Native or Flutter mobile app
- **Wearable Integration**: Apple Health, Google Fit integration
- **Social Features**: Community features and social sharing
- **Advanced AI**: Enhanced AI models and personalization
- **Telehealth Integration**: Healthcare provider collaboration features
- **Advanced Analytics**: Machine learning insights and predictions

---

*This documentation represents the complete NutriCoach application as of August 22, 2025. For updates and additional information, please refer to the project repository and changelog.*