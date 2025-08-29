# NutriCoach Documentation

Comprehensive documentation for the NutriCoach AI-powered nutrition tracking application.

## 📚 Documentation Index

### Core Documentation
- **`COMPLETE_PROGRAM_DOCUMENTATION.md`** – Complete application overview with architecture and features
- **`FEATURE_INDEX.md`** – Comprehensive feature catalog with implementation details
- **`admin_guide.md`** – Administrative interface guide with Docker deployment
- **`mobile_app.md`** – Flutter mobile app documentation and setup guide

### User Guides  
- **`onboarding_guide.md`** – Visual user onboarding walkthrough with screenshots
- **`onboarding_technical_guide.md`** – Technical implementation details for onboarding
- **`user_registration_guide.md`** – Step-by-step user registration and setup

### Developer Resources
- **`scripts.md`** – Maintenance and utility scripts documentation
- **`tests.md`** – Test suite structure, usage, and best practices

## 🚀 Quick Access URLs (Docker Deployment)

### Application Access
- **Main App**: http://localhost:5001
- **Admin Dashboard**: http://localhost:5001/admin/dashboard
- **User Registration**: http://localhost:5001/auth/register
- **API Documentation**: http://localhost:5001/api/docs
- **Health Check**: http://localhost:5001/api/healthz

### API Resources
- **Interactive API Docs (Swagger UI)**: http://localhost:5001/api/docs
- **OpenAPI 3.0 Specification**: http://localhost:5001/openapi.yaml
- **API Endpoints**: http://localhost:5001/api/
  - `/api/logs` - Food logging operations
  - `/api/coach/chat` - AI coaching chat (streaming)
  - `/api/photo/upload` - Photo analysis
  - `/api/analytics/` - Progress and analytics data

## 📁 Screenshots & Visual Documentation

Screenshots are meticulously organized in `docs/screenshots/` by functional area:

### Available Screenshot Collections
- **`admin/`** – Administrative interface and user management
- **`auth/`** – Login and registration flows  
- **`onboarding/`** – 4-step user setup wizard
- **`registration/`** – Complete user registration journey
- **`dashboard/`** – Main application dashboard
- **`food_logging/`** – Food entry and tracking interfaces
- **`ai_coach/`** – AI coaching chat interface
- **`progress_analytics/`** – Charts and progress tracking
- **`settings/`** – User preferences and AI configuration
- **`public_pages/`** – Homepage, privacy policy, terms of service

## 🏗 Architecture Overview

NutriCoach follows modern Flask application patterns:

- **Application Factory**: Proper configuration-based initialization
- **Blueprint Architecture**: 6 main blueprints for logical organization
- **Service Layer**: Clean separation of business logic
- **Privacy-First AI**: Local Ollama integration for data privacy
- **Cross-Platform**: Web app + Flutter mobile companion

## 📦 Recent Updates

### v1.2.0 - Enhanced AI & Mobile Features
- ✅ **Default System Prompts**: Automatic coaching guidance for all users
- ✅ **Flutter Mobile App**: Cross-platform mobile companion
- ✅ **Enhanced Security**: Comprehensive CSRF protection
- ✅ **Streaming AI Chat**: Real-time responses with Server-Sent Events
- ✅ **Docker Optimization**: Production-ready deployment

For detailed release notes and feature documentation, see the individual guide files listed above.