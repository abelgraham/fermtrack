#!/usr/bin/env python3
"""
FermTrack - Fermentation Tracking System - Test User Setup
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

Create test user and bakery for credit system testing
"""

import requests
import json

BASE_URL = 'http://localhost:5000/api'

def create_test_user():
    """Create a test user and bakery"""
    print("🏗️ Setting up test user and bakery...")
    
    # Register a new user
    registration_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'role': 'baker'
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=registration_data)
    
    if response.status_code == 201:
        print("✅ Test user created successfully")
        return True
    elif response.status_code == 409:
        print("ℹ️ Test user already exists")
        return True
    else:
        print(f"❌ Failed to create test user: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_login():
    """Test login with the test user"""
    print("\n🔐 Testing login...")
    
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✅ Login successful")
        token = response.json().get('access_token')
        print(f"   Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

if __name__ == '__main__':
    try:
        if create_test_user():
            token = test_login()
            if token:
                print(f"\n✅ Setup complete! Use token for testing.")
        else:
            print("❌ Setup failed")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the Flask server running?")
    except Exception as e:
        print(f"❌ Setup failed: {e}")