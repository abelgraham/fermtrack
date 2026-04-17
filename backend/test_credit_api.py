#!/usr/bin/env python3
"""
FermTrack - Fermentation Tracking System - Credit API Tests
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

Test script for credit system API integration.
Tests the new credit system endpoints and batch creation with credit limits.
"""

import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000/api'

def test_credit_system_api():
    """Test the credit system through the actual API"""
    print("🧪 Testing Credit System API Integration")
    print("=" * 50)
    
    # Test authentication first
    print("🔐 Testing Authentication...")
    
    # Test login (using correct format with bakery)
    login_data = {
        'username': 'testuser',  # Changed from email to username
        'password': 'testpass123',
        'bakery_slug': 'demo1'  # Add bakery slug
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    token = response.json().get('access_token')
    if not token:
        print("❌ No access token received")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'X-Bakery-Slug': 'demo1'  # Updated to use correct bakery
    }
    
    print("✅ Authentication successful")
    
    # Test credit info endpoint
    print("\n💳 Testing Credit Info Endpoint...")
    
    response = requests.get(f"{BASE_URL}/batches/credits", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Credit info failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    credit_info = response.json().get('credit_info', {})
    print("✅ Credit info retrieved:")
    print(f"   Credit Type: {credit_info.get('credit_type')}")
    print(f"   Credits Used: {credit_info.get('credit_used')}")
    print(f"   Credit Limit: {credit_info.get('credit_limit')}")
    print(f"   Can Create Batch: {credit_info.get('can_create_batch')}")
    print(f"   Is Verified: {credit_info.get('is_verified')}")
    
    # Test batch listing with credit info
    print("\n📋 Testing Batch List with Credit Info...")
    
    response = requests.get(f"{BASE_URL}/batches", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Batch listing failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    batch_data = response.json()
    credit_info = batch_data.get('credit_info', {})
    batches = batch_data.get('batches', [])
    
    print(f"✅ Batch listing successful:")
    print(f"   Total batches: {len(batches)}")
    print(f"   Credit info included: {bool(credit_info)}")
    
    # Test batch creation
    print("\n🍞 Testing Batch Creation with Credit System...")
    
    # Create a test batch
    batch_data = {
        'batch_id': f'credit-test-{int(datetime.now().timestamp())}',
        'recipe_name': 'Credit System Test Bread',
        'dough_weight': 500.0,
        'status': 'mixing',
        'notes': 'Testing credit system integration'
    }
    
    response = requests.post(f"{BASE_URL}/batches", json=batch_data, headers=headers)
    
    if response.status_code == 201:
        print("✅ Batch creation successful:")
        result = response.json()
        batch_info = result.get('batch', {})
        credit_info = result.get('credit_info', {})
        
        print(f"   Batch ID: {batch_info.get('batch_id')}")
        print(f"   Recipe: {batch_info.get('recipe_name')}")
        print(f"   Credits after creation:")
        print(f"     Type: {credit_info.get('credit_type')}")
        print(f"     Used: {credit_info.get('credit_used')}")
        print(f"     Remaining: {credit_info.get('credit_remaining')}")
        
    elif response.status_code == 429:
        print("✅ Credit limit protection working:")
        result = response.json()
        print(f"   Error: {result.get('error')}")
        print(f"   Message: {result.get('message')}")
        credit_info = result.get('credit_info', {})
        print(f"   Credits: {credit_info.get('credit_used')}/{credit_info.get('credit_limit')}")
        
    else:
        print(f"❌ Batch creation failed: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    print("\n✅ Credit System API Test Completed Successfully!")

def test_credit_limits():
    """Test credit limit enforcement by trying to create multiple batches"""
    print("\n🔬 Testing Credit Limit Enforcement")
    print("=" * 40)
    
    # This test would require setting up a bakery with limited credits
    # and attempting to exceed the limit
    print("ℹ️ Credit limit testing requires manual setup of limited bakery")
    print("   Set a bakery to 'limited' with low credit_limit for testing")

if __name__ == '__main__':
    try:
        test_credit_system_api()
        test_credit_limits()
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the Flask server running?")
        print("   Start the server with: python app.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")