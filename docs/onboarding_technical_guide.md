# NutriCoach Complete Onboarding Technical Guide

**Comprehensive Documentation of the 4-Step User Onboarding Process**

*Last Updated: August 22, 2025*

---

## Table of Contents
1. [Overview](#overview)
2. [Pre-Onboarding (Registration)](#pre-onboarding)
3. [4-Step Onboarding Process](#4-step-onboarding)
4. [Post-Onboarding (Dashboard)](#post-onboarding)
5. [Technical Implementation](#technical-implementation)
6. [Troubleshooting](#troubleshooting)

---

## Overview

NutriCoach implements a comprehensive user onboarding system designed to collect essential information for personalized nutrition tracking and AI-powered coaching. The system consists of:

- **Pre-onboarding:** Account registration and legal page access
- **4-step onboarding:** Progressive profile completion
- **Post-onboarding:** Dashboard access with personalized features

### Design Philosophy
- **Progressive Disclosure:** Information collected across multiple focused steps
- **Skip Options:** Users can bypass onboarding for immediate access
- **Personalization:** Each step builds toward customized experience
- **Privacy-First:** Clear legal documentation and consent

---

## Pre-Onboarding

### Homepage Access
**URL:** `/`  
**Template:** `templates/index.html`  
**Features:**
- Welcome message and feature overview
- Call-to-action buttons for registration/login
- Footer links to legal pages
- Responsive design with dark mode support

### User Registration
**URL:** `/auth/register`  
**Template:** `templates/auth/register.html`  
**Form Fields:**
- `username` (string, unique, required)
- `email` (email, unique, required)
- `password` (string, min 8 chars, required)
- `password2` (string, must match password, required)

**Validation:**
- Username: Alphanumeric characters only
- Email: Valid email format, uniqueness check
- Password: Minimum 8 characters with complexity requirements
- Confirmation: Must match original password

**Success Flow:** Redirect to `/onboarding/step1`

### Legal Pages
All accessible without authentication:
- **Privacy Policy** (`/privacy`) - Data collection and usage
- **Terms of Service** (`/terms`) - Usage guidelines and disclaimers
- **Help Center** (`/help`) - Interactive FAQ and support
- **Medical Disclaimer** (`/disclaimer`) - Health information warnings

---

## 4-Step Onboarding

### Step 1: Basic Information
**URL:** `/onboarding/step1`  
**Template:** `templates/onboarding/step1.html`  
**Form:** `BasicInfoForm` (forms/onboarding.py)

**Required Fields:**
- `name` (string) - Full name for personalization
- `age` (integer, 13-120) - For BMR calculations
- `sex` (select: male/female) - For metabolic equations
- `height_cm` (float, 100-250) - For TDEE calculations
- `weight_kg` (float, 30-300) - For current status and targets

**Purpose:** Collect physiological data for accurate calorie and macronutrient calculations using the Mifflin-St Jeor equation.

**Progress:** 25% complete (Step 1 of 4)

### Step 2: Goals & Activity
**URL:** `/onboarding/step2`  
**Template:** `templates/onboarding/step2.html` ✅ (Fixed)
**Form:** `GoalsForm` (forms/onboarding.py)

**Required Fields:**
- `activity_level` (select) - Exercise frequency:
  - `sedentary` - Little/no exercise
  - `light` - 1-3 days/week light exercise
  - `moderate` - 3-5 days/week moderate exercise
  - `active` - 6-7 days/week hard exercise
  - `very_active` - Very hard exercise + physical job

- `goal_type` (select) - Primary objective:
  - `lose` - Weight loss
  - `maintain` - Weight maintenance
  - `gain` - Weight gain

**Optional Fields (conditional):**
- `target_weight_kg` (float) - Goal weight (hidden for "maintain")
- `timeframe_weeks` (integer) - Target timeline (hidden for "maintain")

**Smart Features:**
- Dynamic form: Target weight and timeframe fields appear/disappear based on goal selection
- Visual goal cards explaining safe rates (1-2 lbs/week loss, 0.5-1 lb/week gain)
- TDEE calculation explanation

**Purpose:** Calculate personalized daily calorie and macronutrient targets.

**Progress:** 50% complete (Step 2 of 4)

### Step 3: Lifestyle & Preferences
**URL:** `/onboarding/step3`  
**Template:** `templates/onboarding/step3.html`
**Form:** `LifestyleForm` (forms/onboarding.py)

**Dietary Preferences (Multiple Select):**
- Basic: `omnivore`, `vegetarian`, `vegan`
- Religious: `kosher`, `halal`
- Special: `ketogenic`, `paleo`, `mediterranean`, `low_carb`, `low_fat`

**Allergies & Restrictions (Multiple Select):**
- Nuts: `tree_nuts`, `peanuts`
- Animal: `dairy`, `eggs`, `shellfish`, `fish`
- Other: `soy`, `gluten`, `sesame`

**Lifestyle Factors:**
- `medical_considerations` (text, optional) - Special health needs
- `budget_range` (select: low/medium/high) - Ingredient cost preferences
- `cooking_skill` (select: beginner/intermediate/advanced) - Recipe complexity
- `kitchen_equipment` (multiple select): `stove`, `oven`, `microwave`, `blender`, `air_fryer`, `slow_cooker`
- `meals_per_day` (select: 2-6) - Meal distribution preference
- `sleep_schedule` (select: early_bird/night_owl/flexible) - Timing preferences

**Purpose:** Enable personalized meal recommendations and dietary coaching.

**Progress:** 75% complete (Step 3 of 4)

### Step 4: AI Configuration
**URL:** `/onboarding/step4`  
**Template:** `templates/onboarding/step4.html`
**Form:** `OllamaSettingsForm` (forms/onboarding.py)

**Configuration Fields:**
- `ollama_url` (string, default: "http://localhost:11434") - AI server endpoint
- `default_model` (select) - Preferred AI model (auto-populated)
- `enable_ai_features` (boolean, default: True) - AI coaching toggle

**AI Features Enabled:**
- Personalized nutrition coaching and advice
- Meal planning and recipe suggestions
- Progress analysis and recommendations
- Food photo recognition and logging
- Interactive Q&A about nutrition

**Setup Options:**
1. **Local Ollama** (default) - Maximum privacy, requires local installation
2. **Remote Ollama** - Custom server URL for shared/cloud instances  
3. **Skip AI** - Basic app functionality without AI features

**Connection Testing:** Built-in connectivity validation before completion

**Purpose:** Configure AI-powered coaching and analysis features.

**Progress:** 100% complete (Step 4 of 4)

---

## Post-Onboarding

### Dashboard Welcome
**URL:** `/dashboard`  
**Template:** `templates/dashboard.html` ✅ (Fixed)
**Access:** Authenticated users with completed profiles

**Features:**
- **Daily Summary Cards:** Calories, protein, carbs, fat with progress bars
- **Personalized Targets:** Calculated from onboarding data using:
  - BMR = Mifflin-St Jeor equation (age, sex, height, weight)
  - TDEE = BMR × activity multiplier
  - Goal adjustment = deficit/surplus based on goal type
- **Today's Progress:** Real-time tracking of logged foods
- **Quick Stats:** Streaks, weekly averages, achievement tracking
- **AI Integration:** Personalized recommendations based on profile

### Navigation Available
- **Dashboard** - Daily overview and progress
- **Log Food** - Manual food entry with database search
- **AI Coach** - Interactive nutrition coaching
- **Food Search** - Comprehensive nutrition database
- **Progress** - Analytics, trends, and insights
- **Photo Log** - Camera-based food recognition
- **Settings** - Profile updates and preferences

---

## Technical Implementation

### Backend Architecture

**Models (models.py):**
- `User` - Authentication and basic info
- `UserProfile` - Onboarding data storage
- `FoodEntry` - Nutrition logging
- `SystemLog` - Admin audit trails
- `GlobalSettings` - App-wide configuration

**Forms (forms/onboarding.py):**
- `BasicInfoForm` - Step 1 validation
- `GoalsForm` - Step 2 with dynamic fields
- `LifestyleForm` - Step 3 multi-select handling
- `OllamaSettingsForm` - Step 4 AI configuration

**Routes (routes/onboarding.py):**
- Progressive step validation
- Profile completion tracking
- Skip option handling
- Redirect logic for incomplete profiles

### Frontend Features

**UI/UX:**
- Responsive Tailwind CSS design
- Progress indicators with percentage completion
- Form validation with clear error messages
- Dark mode support throughout
- Professional typography and spacing

**JavaScript Enhancements:**
- Dynamic form field visibility (Step 2 goals)
- Real-time validation feedback
- Progress bar animations
- HTMX for seamless interactions

**Accessibility:**
- Semantic HTML structure
- ARIA labels for screen readers
- Keyboard navigation support
- High contrast color schemes

### Data Flow

1. **Registration** → Create `User` record
2. **Step 1** → Create `UserProfile` with basic info
3. **Step 2** → Calculate and store nutrition targets
4. **Step 3** → Store preferences for meal recommendations
5. **Step 4** → Configure AI settings and model selection
6. **Dashboard** → Display personalized interface with calculated targets

### Calculation Examples

**BMR Calculation (Mifflin-St Jeor):**
- Male: BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) + 5
- Female: BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) - 161

**TDEE Multipliers:**
- Sedentary: BMR × 1.2
- Light: BMR × 1.375
- Moderate: BMR × 1.55
- Active: BMR × 1.725
- Very Active: BMR × 1.9

**Goal Adjustments:**
- Weight Loss: TDEE - 500 (1 lb/week deficit)
- Maintenance: TDEE (no adjustment)
- Weight Gain: TDEE + 500 (1 lb/week surplus)

---

## Troubleshooting

### Common Issues

**Registration Problems:**
- Username already exists → Choose different username
- Invalid email format → Use valid email (user@domain.com)
- Weak password → Include letters, numbers, symbols
- Password mismatch → Ensure passwords match exactly

**Onboarding Issues:**
- Form validation errors → Complete all required fields
- Navigation blocked → Complete current step before proceeding
- Profile incomplete warning → Finish all 4 steps or use skip option

**AI Configuration:**
- Ollama connection failed → Verify Ollama is running on specified URL
- No models detected → Install at least one Ollama model
- Remote server timeout → Check network connectivity and server status

### Support Resources

**Built-in Help:**
- Help Center (`/help`) - Comprehensive FAQ and guides
- Context-sensitive help text on each onboarding step
- Form validation messages with specific requirements

**Legal Documentation:**
- Privacy Policy (`/privacy`) - Data handling and user rights
- Terms of Service (`/terms`) - Usage guidelines and limitations
- Medical Disclaimer (`/disclaimer`) - Health information warnings

### Admin Support

**Admin Dashboard:** `/admin/dashboard`
- User management and profile inspection
- System logs and error tracking
- Ollama configuration and health monitoring
- Onboarding completion statistics

---

## Files and Screenshots

### Documentation Files
- `docs/onboarding_guide.md` - Visual guide with screenshots
- `docs/onboarding_technical_guide.md` - This technical documentation

### Screenshot Files
- `docs/onboarding_01_homepage.png` - Landing page overview
- `docs/onboarding_02_registration.png` - User registration form
- `docs/onboarding_03_login.png` - User login interface
- `docs/onboarding_04_privacy.png` - Privacy policy page
- `docs/onboarding_05_terms.png` - Terms of service page
- `docs/onboarding_06_help.png` - Help center interface
- `docs/onboarding_07_disclaimer.png` - Medical disclaimer page

### Template Files
- `templates/index.html` - Homepage with onboarding entry points
- `templates/auth/register.html` - Registration form
- `templates/auth/login.html` - Login form
- `templates/onboarding/step1.html` - Basic information form
- `templates/onboarding/step2.html` - Goals and activity form ✅
- `templates/onboarding/step3.html` - Lifestyle preferences form
- `templates/onboarding/step4.html` - AI configuration form
- `templates/dashboard.html` - Post-onboarding dashboard ✅

---

*Documentation generated through comprehensive code analysis and automated browser testing*
*All screenshots captured at 1200x800 resolution using Playwright automation*