#!/usr/bin/env python3
"""
FermTrack - Fermentation Tracking System - Applications Table Migration
Copyright (C) 2026 FermTrack Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Database migration script to add user_bakery_applications table
"""

import sqlite3
import os

def create_user_applications_table():
    """Create the user_bakery_applications table"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'fermtrack.db')
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_bakery_applications'")
        if cursor.fetchone():
            print("Table user_bakery_applications already exists")
            return
        
        # Create the table
        cursor.execute("""
            CREATE TABLE user_bakery_applications (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                bakery_id VARCHAR(36) NOT NULL,
                requested_role VARCHAR(20) NOT NULL DEFAULT 'baker',
                status VARCHAR(20) DEFAULT 'pending',
                message TEXT,
                admin_notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                reviewed_at DATETIME,
                reviewed_by_id VARCHAR(36),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (bakery_id) REFERENCES bakeries(id),
                FOREIGN KEY (reviewed_by_id) REFERENCES users(id),
                UNIQUE (user_id, bakery_id)
            )
        """)
        
        conn.commit()
        print("Table user_bakery_applications created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_user_applications_table()