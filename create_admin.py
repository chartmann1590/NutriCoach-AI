#!/usr/bin/env python3
"""
Script to create an admin user and initialize the database with admin-related tables.
"""

import os
import sys
from flask import Flask
from extensions import db
from models import User, GlobalSettings

def create_admin_user():
    """Create an admin user for the system"""
    
    # Create Flask app context
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///nutricoach.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("Admin user already exists!")
            return existing_admin
        
        # Create admin user
        admin_user = User(
            username='admin',
            is_admin=True,
            is_active=True
        )
        admin_user.set_password('admin123')  # Default password - should be changed!
        
        db.session.add(admin_user)
        
        # Create default global settings
        default_settings = [
            ('ollama_url', 'http://74.76.44.128:11434', 'Ollama server URL', 'ollama'),
            ('default_chat_model', 'llama3.1', 'Default chat model name', 'ollama'),
            ('default_vision_model', 'llava', 'Default vision model name', 'ollama'),
            ('model_timeout', '120', 'Model request timeout in seconds', 'ollama'),
            ('max_tokens', '2048', 'Maximum tokens per request', 'ollama'),
            ('temperature', '0.7', 'Model temperature setting', 'ollama'),
            ('app_name', 'NutriCoach', 'Application name', 'general'),
            ('maintenance_mode', 'false', 'Enable maintenance mode', 'general'),
            ('user_registration_enabled', 'true', 'Allow new user registration', 'security'),
            ('max_file_size', '8388608', 'Maximum file upload size in bytes', 'general'),
        ]
        
        for key, value, description, category in default_settings:
            existing_setting = GlobalSettings.query.filter_by(key=key).first()
            if not existing_setting:
                setting = GlobalSettings(
                    key=key,
                    value=value,
                    description=description,
                    category=category,
                    updated_by=admin_user.id
                )
                db.session.add(setting)
        
        db.session.commit()
        
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("Please change the default password after first login!")
        print("Access admin panel at: http://localhost:5001/admin/dashboard")
        
        return admin_user

if __name__ == '__main__':
    create_admin_user()