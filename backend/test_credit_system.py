#!/usr/bin/env python3
"""
Test script for the credit system implementation
"""

import sys
import os
sys.path.append('.')

from app import create_app
from models import db, Bakery
from datetime import datetime, timedelta
import json

def test_credit_system():
    """Test the credit system functionality"""
    app = create_app()
    with app.app_context():
        print("🧪 Testing Credit System Implementation")
        print("=" * 50)
        
        # Get all bakeries
        bakeries = Bakery.query.all()
        print(f"📊 Total bakeries found: {len(bakeries)}")
        
        for bakery in bakeries:
            print(f"\n🏪 Bakery: {bakery.name}")
            print(f"   ID: {bakery.id}")
            print(f"   Verified: {bakery.is_verified}")
            print(f"   Credit Type: {bakery.credit_type}")
            print(f"   Credit Limit: {bakery.credit_limit}")
            print(f"   Credit Used: {bakery.credit_used}")
            print(f"   Credit Remaining: {bakery.get_credit_remaining()}")
            print(f"   Can Create Batch: {bakery.can_create_batch()}")
            
            if bakery.credit_reset_date:
                print(f"   Next Reset: {bakery.credit_reset_date}")
            else:
                print("   Next Reset: Not set")
        
        # Test credit consumption for limited accounts
        print(f"\n🔬 Testing Credit Consumption")
        print("-" * 30)
        
        # Find or create a test bakery with limited credits
        test_bakery = Bakery.query.filter_by(credit_type='limited').first()
        
        if not test_bakery:
            print("📝 Creating test bakery with limited credits...")
            test_bakery = bakeries[0] if bakeries else None
            if test_bakery:
                test_bakery.credit_type = 'limited'
                test_bakery.credit_limit = 3  # Small limit for testing
                test_bakery.credit_used = 0
                test_bakery.credit_reset_date = datetime.now().replace(day=1) + timedelta(days=32)
                # Set to first of next month
                next_month = test_bakery.credit_reset_date.replace(day=1)
                test_bakery.credit_reset_date = next_month
                db.session.commit()
                print(f"✅ Test bakery configured: {test_bakery.name}")
            else:
                print("❌ No bakeries available for testing")
                return
        
        print(f"\n🎯 Testing with bakery: {test_bakery.name}")
        print(f"   Initial credits: {test_bakery.get_credit_remaining()}/{test_bakery.credit_limit}")
        
        # Test credit consumption
        for i in range(test_bakery.credit_limit + 2):  # Try to exceed limit
            can_create = test_bakery.can_create_batch()
            print(f"   Attempt {i+1}: Can create batch? {can_create}")
            
            if can_create:
                test_bakery.consume_credit()
                db.session.commit()
                print(f"     ✅ Credit consumed. Remaining: {test_bakery.get_credit_remaining()}")
            else:
                print(f"     ❌ Credit limit reached!")
                break
        
        # Test monthly reset
        print(f"\n📅 Testing Monthly Reset")
        print("-" * 25)
        print(f"   Before reset - Used: {test_bakery.credit_used}, Remaining: {test_bakery.get_credit_remaining()}")
        
        # Simulate month passing by setting reset date to past
        old_date = test_bakery.credit_reset_date
        test_bakery.credit_reset_date = datetime.now() - timedelta(days=1)
        db.session.commit()
        
        # Check if reset triggers
        test_bakery.reset_credits_if_needed()
        db.session.commit()
        
        print(f"   After reset - Used: {test_bakery.credit_used}, Remaining: {test_bakery.get_credit_remaining()}")
        print(f"   New reset date: {test_bakery.credit_reset_date}")
        
        print(f"\n✅ Credit system test completed!")

if __name__ == '__main__':
    test_credit_system()