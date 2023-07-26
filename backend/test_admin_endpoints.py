#!/usr/bin/env python3

import os
import sys
import django
import requests
import json

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

def test_admin_endpoints():
    """Test admin API endpoints"""
    
    print("Testing Admin API Endpoints...")
    
    # Login as admin
    login_data = {
        "username": "admin",
        "password": "admin123"  # Common admin password
    }
    
    try:
        # First try logging in as admin
        response = requests.post(
            'http://127.0.0.1:8000/api/auth/login/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200:
            print("❌ Admin login failed. Trying alternative credentials...")
            # Try different credentials
            for username, password in [("admin", "password123"), ("instructor1", "instructor123")]:
                login_data = {"username": username, "password": password}
                response = requests.post(
                    'http://127.0.0.1:8000/api/auth/login/',
                    json=login_data,
                    headers={'Content-Type': 'application/json'}
                )
                if response.status_code == 200:
                    print(f"✅ Logged in as {username}")
                    break
            
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access')
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test endpoints
            endpoints = [
                ('/api/admin/users/', 'GET', 'Users API'),
                ('/api/admin/organizations/', 'GET', 'Organizations API'),
                ('/api/admin/stats/', 'GET', 'User Stats API'),
                ('/api/admin/recent-activity/', 'GET', 'Recent Activity API'),
                ('/api/admin/system-overview/', 'GET', 'System Overview API'),
            ]
            
            for endpoint, method, name in endpoints:
                print(f"\n--- Testing {name} ---")
                try:
                    if method == 'GET':
                        test_response = requests.get(
                            f'http://127.0.0.1:8000{endpoint}',
                            headers=headers
                        )
                    
                    print(f"Status Code: {test_response.status_code}")
                    
                    if test_response.status_code == 200:
                        result = test_response.json()
                        if endpoint == '/api/admin/users/':
                            print(f"✅ SUCCESS: Found {len(result.get('users', []))} users")
                        elif endpoint == '/api/admin/organizations/':
                            print(f"✅ SUCCESS: Found {len(result.get('organizations', []))} organizations")
                        elif endpoint == '/api/admin/stats/':
                            print(f"✅ SUCCESS: Total users: {result.get('total_users', 0)}")
                        elif endpoint == '/api/admin/recent-activity/':
                            print(f"✅ SUCCESS: Found {len(result.get('activities', []))} activities")
                        elif endpoint == '/api/admin/system-overview/':
                            print(f"✅ SUCCESS: System overview loaded")
                    else:
                        print(f"❌ FAILED: {test_response.text[:200]}")
                        
                except Exception as e:
                    print(f"❌ ERROR: {e}")
        
        else:
            print(f"❌ Authentication failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_admin_endpoints()
