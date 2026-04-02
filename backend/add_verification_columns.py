#!/usr/bin/env python3
"""
Database migration script to add verification columns to bakeries table
This script handles the case where the columns were removed and need to be re-added
"""

import sqlite3
import os

def add_verification_columns():
    """Add verification columns to the bakeries table if they don't exist"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'fermtrack.db')
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(bakeries)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns
        columns_to_add = [
            ('is_verified', 'BOOLEAN DEFAULT 0'),
            ('verification_status', 'VARCHAR(20) DEFAULT "pending"'),
            ('verification_notes', 'TEXT')
        ]
        
        for column_name, column_def in columns_to_add:
            if column_name not in columns:
                print(f"Adding column: {column_name}")
                cursor.execute(f"ALTER TABLE bakeries ADD COLUMN {column_name} {column_def}")
            else:
                print(f"Column {column_name} already exists")
        
        # Update existing bakeries to be verified (for dev/demo purposes)
        cursor.execute("""
            UPDATE bakeries 
            SET is_verified = 1, verification_status = 'approved', verification_notes = 'Legacy bakery - auto-approved'
            WHERE is_verified IS NULL OR verification_status IS NULL
        """)
        
        conn.commit()
        print("Verification columns added successfully!")
        print("Existing bakeries have been auto-verified for development purposes.")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_verification_columns()