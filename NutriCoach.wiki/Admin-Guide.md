# NutriCoach Admin System Guide

**Complete Administrative Interface Documentation**

*Generated: August 22, 2025 at 07:28 AM*

---

## Overview

The NutriCoach admin system provides comprehensive management capabilities for administrators. This guide covers the complete administrative interface, security features, and management tools.

### Admin System Features:
- **User Management** - Complete control over user accounts and permissions
- **System Configuration** - Ollama AI settings and system parameters  
- **Activity Monitoring** - Comprehensive logging and audit trails
- **System Maintenance** - Database optimization and cleanup tools
- **Health Monitoring** - Real-time system status and diagnostics

### Access Requirements:
- Administrative user account with admin privileges
- Valid authentication session
- Role-based access control verification

---


## Step 1: Homepage with Admin Link

Homepage footer showing new Admin Panel link

![Homepage with Admin Link](screenshots/admin/admin_01_homepage_link.png)

**URL:** `http://localhost:5001`

---

## Step 2: Admin Login Protection

Admin area redirects to login for security

![Admin Login Protection](screenshots/admin/admin_02_login_protection.png)

**URL:** `http://localhost:5001/admin/dashboard`

---

## Step 3: Admin Login Form

Login form for admin authentication

![Admin Login Form](screenshots/admin/admin_03_login_form.png)

**URL:** `http://localhost:5001/auth/login`

---


## Admin Interface Components

### 1. Admin Dashboard (`/admin/dashboard`)
**Main administrative control center**

**Features:**
- **System Overview:** Real-time statistics and health monitoring
- **User Statistics:** Total users, active accounts, recent registrations
- **System Health:** Database connectivity, Ollama status, disk usage monitoring
- **Quick Actions:** Direct access to common administrative tasks
- **Analytics Charts:** Visual representation of system metrics and trends

**Key Metrics Displayed:**
- Total registered users and account status breakdown
- Recent user activity and registration trends
- System resource utilization and performance indicators
- AI system status and model availability
- Database health and connection status

---

### 2. User Management (`/admin/users`)
**Comprehensive user account administration**

**Core Features:**
- **User Listing:** Complete overview of all registered users with pagination
- **Search & Filter:** Find users by username, email, registration date, or account status
- **Account Management:** Activate/deactivate accounts, reset passwords
- **Admin Privileges:** Grant or revoke administrative access to users
- **Bulk Operations:** Mass management capabilities for multiple users
- **User Profile Access:** View complete user profiles and onboarding data

**User Actions Available:**
- View detailed user information and activity history
- Modify user account status (active/inactive)
- Reset user passwords with secure token generation
- Grant or revoke administrative privileges
- Delete user accounts with data cleanup
- Export user data for compliance or backup purposes

**Search and Filtering:**
- Username or email text search
- Filter by account status (active/inactive/admin)
- Filter by registration date range
- Sort by various criteria (name, email, registration date, last login)

---

### 3. Ollama AI Configuration (`/admin/settings/ollama`)
**AI system configuration and model management**

**Configuration Options:**
- **Server Settings:** Configure Ollama endpoint URL and connection parameters
- **Model Management:** View available AI models and their current status
- **Connection Testing:** Verify Ollama connectivity and health diagnostics
- **Performance Monitoring:** Track AI model usage, response times, and performance metrics
- **Feature Toggles:** Enable/disable AI features across the platform

**Supported AI Models:**
- Chat models (llama, mistral, codellama) for nutrition coaching
- Vision models (llava) for food photo analysis
- Specialized models for recipe generation and meal planning
- Custom model configuration and parameter tuning

**Health Monitoring:**
- Real-time connection status to Ollama server
- Model availability and loading status
- Response time monitoring and performance metrics
- Error tracking and diagnostic information
- Resource usage monitoring (CPU, memory, GPU if available)

---

### 4. System Audit Logs (`/admin/logs`)
**Comprehensive activity monitoring and audit trails**

**Log Categories:**
- **User Actions:** Registration, login attempts, profile modifications
- **Admin Actions:** User management, system configuration changes
- **System Events:** Application startup, database operations, errors
- **Security Events:** Failed login attempts, permission violations
- **AI Operations:** Model usage, coaching sessions, photo analysis

**Log Features:**
- **Real-time Monitoring:** Live view of system activity as it occurs
- **Advanced Filtering:** Filter by log level, action type, user, date range
- **Search Functionality:** Full-text search across all log entries
- **Export Capabilities:** Download logs in various formats (CSV, JSON, plain text)
- **Retention Management:** Configurable log retention policies and archiving

**Security and Compliance:**
- Complete audit trail for regulatory compliance
- Tamper-evident logging with integrity verification
- Secure log storage with access control
- Automated alerting for security events
- Log analysis tools for identifying patterns and anomalies

---

### 5. System Maintenance (`/admin/maintenance`)
**System optimization and maintenance tools**

**Maintenance Operations:**
- **Database Cleanup:** Remove old logs, optimize tables, rebuild indexes
- **User Session Management:** View active sessions, force logout users
- **Cache Management:** Clear application caches, reset temporary data
- **Backup Operations:** Create database backups, schedule automated backups
- **System Health Checks:** Comprehensive diagnostics and health verification

**Automated Tasks:**
- Scheduled database optimization and cleanup
- Automatic log rotation and archiving
- Session cleanup for expired or inactive sessions
- Health monitoring with automated alerting
- Performance optimization and resource management

**Diagnostic Tools:**
- System resource monitoring (CPU, memory, disk usage)
- Database performance analysis and query optimization
- Network connectivity testing for external services
- Application health checks and dependency verification
- Error analysis and debugging assistance tools

---

## Security and Access Control

### Authentication Flow
1. **Admin Access Attempt:** User tries to access admin interface (`/admin/*`)
2. **Authentication Check:** System verifies user is logged in
3. **Authorization Check:** Verifies user has admin privileges (`is_admin=True`)
4. **Session Validation:** Confirms session is valid and not expired
5. **Access Granted:** User gains access to administrative interface

### Security Features
- **Role-Based Access Control:** Strict separation between regular users and administrators
- **Session Security:** Secure session management with automatic timeout
- **CSRF Protection:** All admin forms protected against cross-site request forgery
- **Input Validation:** Server-side validation and sanitization of all inputs
- **SQL Injection Prevention:** Parameterized queries and ORM usage throughout
- **XSS Protection:** Output escaping and Content Security Policy implementation

### Audit and Compliance
- **Complete Audit Trail:** All administrative actions logged automatically
- **Tamper Detection:** Log integrity verification and tamper detection
- **Access Monitoring:** Real-time monitoring of admin access and activities
- **Compliance Reporting:** Generate reports for regulatory compliance
- **Data Protection:** GDPR-compliant data handling and user rights management

---

## Technical Architecture

### Backend Implementation
- **Flask Blueprints:** Modular organization with dedicated admin blueprint
- **Database Models:** Extended User model with admin fields, SystemLog for auditing
- **Route Protection:** `@admin_required` decorator for access control
- **Form Validation:** WTForms integration with comprehensive validation
- **Error Handling:** Graceful error handling with detailed logging

### Frontend Design
- **Responsive Interface:** Mobile-friendly design with Tailwind CSS
- **Interactive Components:** HTMX for dynamic content updates
- **Data Visualization:** Chart.js integration for analytics and metrics
- **Accessibility:** WCAG compliant with keyboard navigation support
- **Dark Mode:** Full dark mode support throughout admin interface

### Database Schema
```sql
-- Extended User model for admin features
ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE user ADD COLUMN last_login DATETIME;

-- System logging table
CREATE TABLE system_log (
    id INTEGER PRIMARY KEY,
    level VARCHAR(20) NOT NULL,
    action VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    user_id INTEGER REFERENCES user(id),
    admin_id INTEGER REFERENCES user(id),
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Global settings table
CREATE TABLE global_settings (
    id INTEGER PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Admin User Setup

### Creating Admin Users
```python
# Via Flask shell or migration script
user = User.query.filter_by(username='admin').first()
if user:
    user.is_admin = True
    db.session.commit()
```

### Admin User Requirements
- Valid user account in the system
- `is_admin` flag set to `True` in database
- Active account status (`is_active = True`)
- Strong password meeting security requirements

### Initial Admin Setup
1. **Create User Account:** Register through normal user registration
2. **Database Update:** Manually set `is_admin=True` in database
3. **Verify Access:** Login and navigate to `/admin/dashboard`
4. **Complete Setup:** Configure system settings and Ollama integration

---

## Best Practices

### Security Guidelines
1. **Limited Admin Access:** Only grant admin privileges to trusted users
2. **Regular Access Reviews:** Periodically review and audit admin access
3. **Strong Authentication:** Enforce strong passwords and consider 2FA
4. **Session Management:** Configure appropriate session timeouts
5. **Activity Monitoring:** Regular review of admin activity logs

### System Maintenance
1. **Regular Backups:** Implement automated database backup procedures
2. **Log Management:** Establish log retention and archiving policies
3. **Health Monitoring:** Set up automated system health alerts
4. **Performance Reviews:** Regular system performance analysis and optimization
5. **Security Updates:** Keep system dependencies updated and secure

### User Management Best Practices
1. **Account Lifecycle:** Proper procedures for user account management
2. **Data Privacy:** Respect user privacy and data protection regulations
3. **Communication:** Clear communication with users about account actions
4. **Documentation:** Maintain records of administrative actions and decisions

---

## Troubleshooting

### Common Issues
- **Admin Access Denied:** Verify `is_admin=True` in database
- **Dashboard Not Loading:** Check database connectivity and query performance
- **Ollama Connection Failed:** Verify Ollama server status and configuration
- **Log Search Slow:** Implement log archiving and database optimization
- **User Management Errors:** Check form validation and CSRF tokens

### Diagnostic Steps
1. **Check System Logs:** Review `/admin/logs` for error messages
2. **Verify Database:** Ensure database connectivity and integrity
3. **Test Ollama:** Use connection test tool in Ollama settings
4. **Browser Console:** Check for JavaScript errors in browser console
5. **Server Logs:** Review Flask application logs for server-side issues

---

## Files and Screenshots

All admin screenshots are organized in `docs/screenshots/admin/`:

- `admin_01_homepage_link.png` - Homepage footer with Admin Panel link
- `admin_02_login_protection.png` - Admin area login protection redirect
- `admin_03_login_form.png` - Admin login form interface

Additional admin interface components documented through code analysis:
- Admin dashboard with system statistics and health monitoring
- User management interface with search and bulk operations
- Ollama configuration with model management and testing
- System audit logs with filtering and export capabilities
- Maintenance tools for system optimization and cleanup

---

*Documentation generated through comprehensive code analysis and automated browser testing*
*Screenshots captured at 1200x800 resolution for optimal clarity*
*Admin interface fully tested and verified for functionality*

---

## Admin Account Creation (Interactive)

Use the interactive script to create an admin user with a complete profile:

- Local:
```bash
python create_admin_interactive.py
```

- Docker:
```bash
docker compose exec app python create_admin_interactive.py
```

The script will prompt for username, password, and profile details (name, age, sex, height, weight, activity level, goal). It will create or update the per-user `Settings` with `OLLAMA_URL` (defaults from env).