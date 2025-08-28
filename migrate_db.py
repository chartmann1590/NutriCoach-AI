#!/usr/bin/env python3
"""
Database migration script to add admin functionality
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add admin columns to existing database"""
    
    db_path = 'instance/nutricoach.db'
    
    if not os.path.exists(db_path):
        print("Database doesn't exist. Creating new one...")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'is_admin' not in columns:
            print("Adding is_admin column...")
            cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0 NOT NULL")
        
        if 'is_active' not in columns:
            print("Adding is_active column...")
            cursor.execute("ALTER TABLE user ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL")
        
        if 'last_login' not in columns:
            print("Adding last_login column...")
            cursor.execute("ALTER TABLE user ADD COLUMN last_login DATETIME")
        
        # Create new tables
        print("Creating SystemLog table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level VARCHAR(20) NOT NULL,
                action VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                user_id INTEGER,
                admin_id INTEGER,
                ip_address VARCHAR(45),
                user_agent TEXT,
                extra_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (admin_id) REFERENCES user(id)
            )
        """)
        
        print("Creating GlobalSettings table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS global_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key VARCHAR(100) UNIQUE NOT NULL,
                value TEXT,
                description TEXT,
                category VARCHAR(50) DEFAULT 'general',
                updated_by INTEGER,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (updated_by) REFERENCES user(id)
            )
        """)
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()