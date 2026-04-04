#!/usr/bin/env python3
"""
Simple test to verify credit system columns exist in database
"""

import sqlite3
import os

def check_database_schema():
    """Check if credit system columns exist in the database"""
    db_path = 'fermtrack.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    print(f"🔍 Checking database schema: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info for bakeries
        cursor.execute("PRAGMA table_info(bakeries)")
        columns = cursor.fetchall()
        
        print("\n📋 Bakeries table columns:")
        credit_columns = []
        for col in columns:
            col_name = col[1]  # Column name is at index 1
            col_type = col[2]  # Column type is at index 2
            print(f"   {col_name}: {col_type}")
            
            if col_name.startswith('credit_'):
                credit_columns.append(col_name)
        
        print(f"\n🎯 Credit system columns found: {credit_columns}")
        
        required_columns = ['credit_type', 'credit_limit', 'credit_used', 'credit_reset_date']
        missing_columns = [col for col in required_columns if col not in credit_columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        else:
            print("✅ All required credit system columns exist!")
            
            # Test a simple query
            cursor.execute("SELECT id, name, credit_type, credit_limit, credit_used FROM bakeries")
            bakeries = cursor.fetchall()
            
            print(f"\n📊 Bakery data ({len(bakeries)} records):")
            for bakery in bakeries:
                print(f"   {bakery[1]}: {bakery[2]} ({bakery[4]}/{bakery[3]} credits used)")
            
            return True
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    check_database_schema()