#!/usr/bin/env python3
"""
Quick script to make an existing user admin
"""

import sqlite3

def make_user_admin(username):
    """Make an existing user admin"""
    
    db_path = 'instance/nutricoach.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Update user to be admin
        cursor.execute("UPDATE user SET is_admin = 1 WHERE username = ?", (username,))
        
        if cursor.rowcount > 0:
            conn.commit()
            print(f"User '{username}' is now an admin!")
        else:
            print(f"User '{username}' not found!")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    # Try to make existing test users admin
    test_users = ['e2euser', 'testuser', 'admintest', 'regularuser']
    
    for username in test_users:
        make_user_admin(username)