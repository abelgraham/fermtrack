#!/usr/bin/env python3
"""
Simple API test script for FermTrack Backend

Tests basic API functionality including authentication and batch operations.
Run this script after starting the FermTrack backend server.
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = 'http://localhost:5000/api'

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/health')
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: Cannot connect to server - {e}")
        return False

def test_user_registration_and_login():
    """Test user registration and login"""
    # Test registration
    test_user = {
        "username": f"testuser_{int(datetime.now().timestamp())}",
        "email": f"test_{int(datetime.now().timestamp())}@example.com",
        "password": "testpassword123",
        "role": "baker"
    }
    
    try:
        # Register user
        response = requests.post(f'{BASE_URL}/auth/register', json=test_user)
        if response.status_code == 201:
            print("✅ User registration successful")
            data = response.json()
            token = data['access_token']
            
            # Test login
            login_data = {
                "username": test_user["username"],
                "password": test_user["password"]
            }
            
            response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
            if response.status_code == 200:
                print("✅ User login successful")
                return token
            else:
                print(f"❌ User login failed: {response.status_code}")
                return None
        else:
            print(f"❌ User registration failed: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Authentication test failed: {e}")
        return None

def test_batch_operations(token):
    """Test batch creation and operations"""
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create batch
    batch_data = {
        "batch_id": f"TEST_{int(datetime.now().timestamp())}",
        "recipe_name": "Test Pretzel Dough",
        "dough_weight": 1500.0,
        "temperature": 22.5,
        "humidity": 65.0,
        "notes": "Test batch for API validation"
    }
    
    try:
        # Create batch
        response = requests.post(f'{BASE_URL}/batches', json=batch_data, headers=headers)
        if response.status_code == 201:
            print("✅ Batch creation successful")
            batch = response.json()['batch']
            batch_id = batch['batch_id']
            
            # Add action to batch
            action_data = {
                "action_type": "fortify",
                "description": "Test fortification action",
                "weight_change": 25.0,
                "temperature_recorded": 23.0
            }
            
            response = requests.post(f'{BASE_URL}/batches/{batch_id}/actions', 
                                   json=action_data, headers=headers)
            if response.status_code == 201:
                print("✅ Batch action addition successful")
                
                # Add fermentation stage
                stage_data = {
                    "stage_name": "bulk_ferment",
                    "target_duration_hours": 4.0,
                    "temperature_target": 24.0,
                    "notes": "Test bulk fermentation"
                }
                
                response = requests.post(f'{BASE_URL}/batches/{batch_id}/fermentation-stages',
                                       json=stage_data, headers=headers)
                if response.status_code == 201:
                    print("✅ Fermentation stage addition successful")
                    
                    # List batches
                    response = requests.get(f'{BASE_URL}/batches', headers=headers)
                    if response.status_code == 200:
                        batches = response.json()['batches']
                        print(f"✅ Batch listing successful ({len(batches)} batches found)")
                        return True
                    else:
                        print(f"❌ Batch listing failed: {response.status_code}")
                else:
                    print(f"❌ Fermentation stage addition failed: {response.status_code}")
            else:
                print(f"❌ Batch action addition failed: {response.status_code}")
        else:
            print(f"❌ Batch creation failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Batch operations test failed: {e}")
        
    return False

def test_admin_login():
    """Test default admin login"""
    admin_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/login', json=admin_data)
        if response.status_code == 200:
            print("✅ Default admin login successful")
            data = response.json()
            return data['access_token']
        else:
            print(f"❌ Default admin login failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Admin login test failed: {e}")
        return None

def main():
    """Run all tests"""
    print("🧪 Running FermTrack Backend API Tests")
    print("="*50)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Server is not running or not reachable.")
        print("Please start the server with: python app.py")
        return 1
    
    print()
    
    # Test admin login
    admin_token = test_admin_login()
    if not admin_token:
        return 1
    
    print()
    
    # Test user operations
    user_token = test_user_registration_and_login()
    if not user_token:
        return 1
    
    print()
    
    # Test batch operations
    if not test_batch_operations(user_token):
        return 1
    
    print()
    print("="*50)
    print("🎉 All tests passed! FermTrack API is working correctly.")
    print("="*50)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())