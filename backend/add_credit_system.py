#!/usr/bin/env python3
"""
Database migration to add credit system fields to bakeries table
"""

import sqlite3
import os
from datetime import datetime

def add_credit_columns():
    """Add credit system columns to existing bakeries"""
    
    # Find the database file
    db_path = None
    possible_paths = [
        'fermtrack.db',
        '../fermtrack.db',
        '../instance/fermtrack.db',
        'instance/fermtrack.db',
        '/var/lib/fermtrack/fermtrack.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Could not find database file")
        return False
    
    print(f"📁 Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if credit columns already exist
        cursor.execute("PRAGMA table_info(bakeries)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add credit_type column if it doesn't exist
        if 'credit_type' not in columns:
            print("➕ Adding credit_type column...")
            cursor.execute("ALTER TABLE bakeries ADD COLUMN credit_type TEXT DEFAULT 'limited'")
        
        # Add credit_limit column if it doesn't exist  
        if 'credit_limit' not in columns:
            print("➕ Adding credit_limit column...")
            cursor.execute("ALTER TABLE bakeries ADD COLUMN credit_limit INTEGER DEFAULT 10")
        
        # Add credit_used column if it doesn't exist
        if 'credit_used' not in columns:
            print("➕ Adding credit_used column...")
            cursor.execute("ALTER TABLE bakeries ADD COLUMN credit_used INTEGER DEFAULT 0")
        
        # Add credit_reset_date column if it doesn't exist
        if 'credit_reset_date' not in columns:
            print("➕ Adding credit_reset_date column...")
            cursor.execute("ALTER TABLE bakeries ADD COLUMN credit_reset_date DATETIME")
            
            # Set initial reset date to first day of next month for all bakeries
            cursor.execute("""
                UPDATE bakeries 
                SET credit_reset_date = date('now', 'start of month', '+1 month')
                WHERE credit_reset_date IS NULL
            """)
        
        # Set default values for existing bakeries
        print("🔧 Setting default credit values for existing bakeries...")
        
        # Verified bakeries get unlimited credits by default
        cursor.execute("""
            UPDATE bakeries 
            SET credit_type = 'unlimited'
            WHERE is_verified = 1 AND (credit_type IS NULL OR credit_type = 'limited')
        """)
        
        # Unverified bakeries get limited credits
        cursor.execute("""
            UPDATE bakeries 
            SET credit_type = 'limited', credit_limit = 10
            WHERE is_verified = 0 AND (credit_type IS NULL OR credit_type = 'unlimited')
        """)
        
        # Set credit_used to 0 for all bakeries if null
        cursor.execute("""
            UPDATE bakeries 
            SET credit_used = 0 
            WHERE credit_used IS NULL
        """)
        
        conn.commit()
        
        # Verify the changes
        cursor.execute("SELECT COUNT(*) FROM bakeries")
        total_bakeries = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bakeries WHERE credit_type = 'unlimited'")
        unlimited_bakeries = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bakeries WHERE credit_type = 'limited'")
        limited_bakeries = cursor.fetchone()[0]
        
        print(f"✅ Migration completed successfully!")
        print(f"   📊 Total bakeries: {total_bakeries}")
        print(f"   🔓 Unlimited credit accounts: {unlimited_bakeries}")
        print(f"   📏 Limited credit accounts: {limited_bakeries}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting credit system migration...")
    success = add_credit_columns()
    
    if success:
        print("\n🎉 Credit system migration completed successfully!")
        print("📝 Summary:")
        print("   • Added credit_type column (limited/unlimited)")
        print("   • Added credit_limit column (monthly limit)")
        print("   • Added credit_used column (current usage)")
        print("   • Added credit_reset_date column (monthly reset)")
        print("   • Verified bakeries → unlimited credits")
        print("   • Unverified bakeries → limited credits (10/month)")
    else:
        print("\n💥 Migration failed! Check the error messages above.")