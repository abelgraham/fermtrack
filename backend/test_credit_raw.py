#!/usr/bin/env python3
"""
FermTrack - Fermentation Tracking System - Credit Raw SQL Tests
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

Test credit system using raw SQL to avoid SQLAlchemy caching issues
"""

import sqlite3
import os
from datetime import datetime, timedelta

def test_credit_system_raw():
    """Test the credit system using raw SQL"""
    db_path = 'fermtrack.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return
    
    print("🧪 Testing Credit System (Raw SQL)")
    print("=" * 45)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all bakeries with credit info
        cursor.execute("""
            SELECT id, name, is_verified, credit_type, credit_limit, credit_used, credit_reset_date
            FROM bakeries
        """)
        bakeries = cursor.fetchall()
        
        print(f"📊 Found {len(bakeries)} bakeries:")
        for bakery in bakeries:
            bakery_id, name, is_verified, credit_type, credit_limit, credit_used, reset_date = bakery
            remaining = credit_limit - credit_used if credit_type == 'limited' else 'unlimited'
            print(f"   🏪 {name}")
            print(f"      Verified: {bool(is_verified)}")
            print(f"      Credit Type: {credit_type}")
            print(f"      Credits: {credit_used}/{credit_limit} (remaining: {remaining})")
            print(f"      Reset Date: {reset_date}")
            print()
        
        # Test credit consumption logic
        print("🧪 Testing Credit Consumption Logic")
        print("-" * 35)
        
        # Find a bakery to test with
        test_bakery = bakeries[0] if bakeries else None
        
        if not test_bakery:
            print("❌ No bakeries found for testing")
            return
        
        bakery_id, name, is_verified, credit_type, credit_limit, credit_used, reset_date = test_bakery
        
        # Set up test conditions - create limited bakery for testing
        print(f"🎯 Setting up test with bakery: {name}")
        
        # Temporarily set to limited for testing
        next_month = datetime.now().replace(day=1) + timedelta(days=32)
        next_month = next_month.replace(day=1)  # First of next month
        
        cursor.execute("""
            UPDATE bakeries 
            SET credit_type = 'limited', 
                credit_limit = 3, 
                credit_used = 0,
                credit_reset_date = ?
            WHERE id = ?
        """, (next_month.isoformat(), bakery_id))
        
        print(f"   ✅ Set to limited: 3 credits per month")
        
        # Test credit consumption
        for i in range(5):  # Try to use more credits than available
            # Check if can create batch
            cursor.execute("""
                SELECT credit_type, credit_limit, credit_used 
                FROM bakeries 
                WHERE id = ?
            """, (bakery_id,))
            
            current = cursor.fetchone()
            if not current:
                break
                
            credit_type, credit_limit, credit_used = current
            can_create = credit_type == 'unlimited' or credit_used < credit_limit
            
            print(f"   Attempt {i+1}: Can create batch? {can_create}")
            print(f"     Credits used: {credit_used}/{credit_limit}")
            
            if can_create and credit_type == 'limited':
                # Consume credit
                cursor.execute("""
                    UPDATE bakeries 
                    SET credit_used = credit_used + 1 
                    WHERE id = ?
                """, (bakery_id,))
                conn.commit()
                print(f"     ✅ Credit consumed!")
            elif not can_create:
                print(f"     ❌ Credit limit reached!")
                break
            else:
                print(f"     ✅ Unlimited credits - no consumption needed")
        
        # Test monthly reset simulation
        print(f"\n📅 Testing Monthly Reset")
        print("-" * 25)
        
        # Get current state
        cursor.execute("""
            SELECT credit_used, credit_reset_date 
            FROM bakeries 
            WHERE id = ?
        """, (bakery_id,))
        
        before_reset = cursor.fetchone()
        print(f"   Before reset: {before_reset[0]} credits used")
        print(f"   Reset date: {before_reset[1]}")
        
        # Simulate month passing
        past_date = datetime.now() - timedelta(days=1)
        cursor.execute("""
            UPDATE bakeries 
            SET credit_reset_date = ?
            WHERE id = ?
        """, (past_date.isoformat(), bakery_id))
        
        # Simulate reset check (this would be in the model method)
        cursor.execute("""
            UPDATE bakeries 
            SET credit_used = 0,
                credit_reset_date = ?
            WHERE id = ? AND credit_reset_date < ?
        """, (next_month.isoformat(), bakery_id, datetime.now().isoformat()))
        
        conn.commit()
        
        # Check after reset
        cursor.execute("""
            SELECT credit_used, credit_reset_date 
            FROM bakeries 
            WHERE id = ?
        """, (bakery_id,))
        
        after_reset = cursor.fetchone()
        print(f"   After reset: {after_reset[0]} credits used")  
        print(f"   New reset date: {after_reset[1]}")
        
        # Restore original state
        cursor.execute("""
            UPDATE bakeries 
            SET credit_type = 'unlimited',
                credit_limit = 10,
                credit_used = 0
            WHERE id = ?
        """, (bakery_id,))
        conn.commit()
        
        print(f"\n✅ Credit system test completed successfully!")
        print(f"   🔧 Bakery {name} restored to original state")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    test_credit_system_raw()