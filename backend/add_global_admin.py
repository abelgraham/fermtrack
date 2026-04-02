#!/usr/bin/env python3
"""
Database migration script to add is_global_admin column to users table
and create a default global admin user.
"""

import sqlite3
import sys
import os
from werkzeug.security import generate_password_hash

def add_global_admin_column(db_path):
    """Add is_global_admin column to users table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column exists
        cursor.execute("PRAGMA table_info(users);")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_global_admin' not in columns:
            print(f"Adding is_global_admin column to {db_path}...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_global_admin BOOLEAN DEFAULT 0;")
            conn.commit()
            print("✅ Added is_global_admin column")
        else:
            print(f"✅ is_global_admin column already exists in {db_path}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error updating {db_path}: {e}")
        return False
    
    return True

def create_global_admin(db_path):
    """Create a global admin user if it doesn't exist"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if admin user exists
        cursor.execute("SELECT id FROM users WHERE username = 'admin';")
        if cursor.fetchone():
            # Update existing admin to be global admin
            print(f"Updating existing admin user to global admin in {db_path}...")
            cursor.execute("""
                UPDATE users 
                SET is_global_admin = 1 
                WHERE username = 'admin';
            """)
        else:
            # Create new admin user
            print(f"Creating global admin user in {db_path}...")
            admin_id = 'admin-user-global-' + str(hash(db_path))[-8:]
            password_hash = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, is_active, is_global_admin)
                VALUES (?, 'admin', 'admin@fermtrack.local', ?, 1, 1);
            """, (admin_id, password_hash))
        
        conn.commit()
        conn.close()
        print("✅ Global admin user configured")
        
    except Exception as e:
        print(f"❌ Error creating global admin in {db_path}: {e}")
        return False
    
    return True

def main():
    """Main function to run migrations"""
    # Database paths
    db_paths = [
        "/home/ag/fermtrack/backend/instance/fermtrack.db",
        "/home/ag/fermtrack/backend/fermtrack.db", 
        "/home/ag/fermtrack/instance/fermtrack.db"
    ]
    
    print("🔧 Migrating databases for global admin support...")
    
    success_count = 0
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"\n📂 Processing: {db_path}")
            if add_global_admin_column(db_path) and create_global_admin(db_path):
                success_count += 1
        else:
            print(f"⚠️  Database not found: {db_path}")
    
    if success_count > 0:
        print(f"\n🎉 Migration completed successfully for {success_count} database(s)")
        print("👤 Global admin login: admin / admin123")
        print("🔑 Global admins can login without specifying a bakery")
    else:
        print("\n❌ Migration failed")
        sys.exit(1)

if __name__ == "__main__":
    main()