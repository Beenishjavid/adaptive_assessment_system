#!/usr/bin/env python
"""
Comprehensive test script for admin API endpoints with proper authentication
"""
import os
import sys
import django
import requests
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

def get_admin_token():
    """Get JWT token for admin user"""
    try:
        # Try to authenticate as admin
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            print("❌ No admin user found")
            return None
        
        # Generate JWT token
        refresh = RefreshToken.for_user(admin_user)
        access_token = str(refresh.access_token)
        print(f"✅ Generated token for admin user: {admin_user.username}")
        return access_token
    except Exception as e:
        print(f"❌ Error getting admin token: {e}")
        return None

def test_endpoint(url, token, endpoint_name):
    """Test a single endpoint"""
    try:
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        response = requests.get(f'http://127.0.0.1:8000{url}', headers=headers)
        
        print(f"\n--- Testing {endpoint_name} ---")
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'users' in data:
                    print(f"✅ SUCCESS: Found {len(data['users'])} users")
                elif 'organizations' in data:
                    print(f"✅ SUCCESS: Found {len(data['organizations'])} organizations")
                elif 'total_users' in data:
                    print(f"✅ SUCCESS: Total users: {data.get('total_users', 'N/A')}")
                elif 'activities' in data:
                    print(f"✅ SUCCESS: Found {len(data['activities'])} activities")
                elif 'user_stats' in data or 'quiz_stats' in data:
                    print(f"✅ SUCCESS: System overview loaded")
                else:
                    print(f"✅ SUCCESS: Response received")
                    print(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Non-dict response'}")
            except Exception as e:
                print(f"✅ SUCCESS: Non-JSON response (Status 200)")
        else:
            print(f"❌ FAILED: {response.text[:200]}...")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    print("=== Comprehensive Admin API Test ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get admin token
    token = get_admin_token()
    if not token:
        print("Cannot proceed without admin token")
        return
    
    # Test endpoints
    endpoints = [
        ('/api/admin/users/', 'Users API'),
        ('/api/admin/organizations/', 'Organizations API'),
        ('/api/admin/stats/', 'User Stats API'),
        ('/api/admin/recent-activity/', 'Recent Activity API'),
        ('/api/admin/system-overview/', 'System Overview API'),
    ]
    
    results = {}
    for url, name in endpoints:
        results[name] = test_endpoint(url, token, name)
    
    # Summary
    print(f"\n=== TEST SUMMARY ===")
    passed = sum(results.values())
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {name}")

if __name__ == '__main__':
    main()
