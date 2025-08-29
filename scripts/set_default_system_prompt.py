#!/usr/bin/env python3
"""
Script to set default system prompt for users who have blank or null system prompts.
This ensures all users have a system prompt, but preserves any custom prompts users have set.
Only affects users with blank/null system prompts - does not override user customizations.
"""

import sys
import os

# Add the parent directory to the Python path so we can import from the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import User, Settings
from extensions import db
from constants import DEFAULT_SYSTEM_PROMPT


def update_system_prompts():
    """Update users with blank or null system prompts to use the default."""
    
    app = create_app()
    with app.app_context():
        try:
            # Find settings with blank or null system prompts
            settings_to_update = Settings.query.filter(
                db.or_(
                    Settings.system_prompt.is_(None),
                    Settings.system_prompt == '',
                    Settings.system_prompt == ' '
                )
            ).all()
            
            if not settings_to_update:
                print("All users already have system prompts set.")
                return
            
            print(f"Found {len(settings_to_update)} users with blank system prompts.")
            
            # Update each settings record
            updated_count = 0
            for settings in settings_to_update:
                user = User.query.get(settings.user_id)
                if user:
                    print(f"  Updating system prompt for user: {user.username}")
                    settings.system_prompt = DEFAULT_SYSTEM_PROMPT
                    updated_count += 1
                else:
                    print(f"  Warning: Found settings without valid user (ID: {settings.user_id})")
            
            # Commit changes
            db.session.commit()
            print(f"✓ Successfully updated {updated_count} user system prompts.")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error updating system prompts: {e}")
            return False
    
    return True


def create_missing_settings():
    """Create Settings records for users who don't have them."""
    
    app = create_app()
    with app.app_context():
        try:
            # Find users without settings
            users_without_settings = User.query.filter(
                ~User.id.in_(
                    db.session.query(Settings.user_id)
                )
            ).all()
            
            if not users_without_settings:
                print("✓ All users have settings records.")
                return
            
            print(f"Found {len(users_without_settings)} users without settings.")
            
            # Create settings for these users
            created_count = 0
            for user in users_without_settings:
                print(f"  Creating settings for user: {user.username}")
                
                settings = Settings(
                    user_id=user.id,
                    ollama_url='http://localhost:11434',
                    system_prompt=DEFAULT_SYSTEM_PROMPT,
                    safety_mode=True
                )
                
                db.session.add(settings)
                created_count += 1
            
            # Commit changes
            db.session.commit()
            print(f"✓ Successfully created settings for {created_count} users.")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error creating settings: {e}")
            return False
    
    return True


if __name__ == '__main__':
    print("=== Setting Default System Prompts ===")
    print()
    
    # First create any missing settings records
    print("Step 1: Creating missing settings records...")
    if not create_missing_settings():
        print("Failed to create missing settings. Exiting.")
        sys.exit(1)
    
    print()
    
    # Then update system prompts
    print("Step 2: Updating blank system prompts...")
    if not update_system_prompts():
        print("Failed to update system prompts. Exiting.")
        sys.exit(1)
    
    print()
    print("=== All Done! ===")
    print("All users now have the default system prompt set.")