#!/usr/bin/env python3
"""
Create admin user with profile for testing
"""

import sqlite3

def create_admin_with_profile():
    """Create or update admin user with profile"""
    
    db_path = 'instance/nutricoach.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Make sure user is admin
        cursor.execute("UPDATE user SET is_admin = 1 WHERE username = ?", ('e2euser',))
        
        # Get user ID
        cursor.execute("SELECT id FROM user WHERE username = ?", ('e2euser',))
        user_result = cursor.fetchone()
        
        if not user_result:
            print("User 'e2euser' not found!")
            return
            
        user_id = user_result[0]
        print(f"Found user ID: {user_id}")
        
        # Check if profile exists
        cursor.execute("SELECT id FROM profile WHERE user_id = ?", (user_id,))
        profile_result = cursor.fetchone()
        
        if profile_result:
            print("Profile already exists for user")
        else:
            # Create profile
            cursor.execute("""
                INSERT INTO profile (user_id, name, age, sex, height_cm, weight_kg, 
                                   activity_level, goal_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (user_id, 'E2E Test Admin', 30, 'male', 175, 75, 'moderate', 'maintain'))
            print("Profile created for admin user")
        
        # Check if settings exist
        cursor.execute("SELECT id FROM settings WHERE user_id = ?", (user_id,))
        settings_result = cursor.fetchone()
        
        if not settings_result:
            # Create settings
            cursor.execute("""
                INSERT INTO settings (user_id, ollama_url, system_prompt, safety_mode)
                VALUES (?, ?, ?, ?)
            """, (user_id, 'http://localhost:11434', 'You are a helpful nutrition coach.', 1))
            print("Settings created for admin user")
        
        conn.commit()
        print("Admin user setup completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    create_admin_with_profile()