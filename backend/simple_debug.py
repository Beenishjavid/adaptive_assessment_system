#!/usr/bin/env python
"""
Quick API Debug Test
"""
import requests

BASE_URL = 'http://127.0.0.1:8000'

def test_endpoints():
    """Test API endpoints directly"""
    
    # Test authentication first
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    print("Testing login...")
    try:
        response = requests.post(f'{BASE_URL}/api/auth/login/', json=login_data)
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            token = response.json().get('access')
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test admin endpoints
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    endpoints = [
        '/api/admin/users/',
        '/api/admin/organizations/',
        '/api/admin/recent-activity/',
        '/api/admin/system-overview/',
        '/api/groups/',
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting {endpoint}...")
            response = requests.get(f'{BASE_URL}{endpoint}', headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code >= 400:
                print(f"Error: {response.text[:200]}...")
            else:
                print("✅ Success")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == '__main__':
    test_endpoints()
