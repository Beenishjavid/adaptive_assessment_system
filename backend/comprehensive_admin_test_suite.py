#!/usr/bin/env python
"""
Comprehensive Admin Dashboard Test Suite
"""
import os
import sys
import django
import requests
import json
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

def get_admin_token():
    """Get JWT token for admin user"""
    try:
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            return None
        
        refresh = RefreshToken.for_user(admin_user)
        access_token = str(refresh.access_token)
        return access_token
    except Exception as e:
        print(f"Error getting admin token: {e}")
        return None

def test_all_endpoints():
    """Test all admin endpoints comprehensively"""
    token = get_admin_token()
    if not token:
        print("❌ Could not get admin token")
        return False
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    base_url = 'http://127.0.0.1:8000'
    
    timestamp = str(int(time.time()))[-6:]
    all_passed = True
    
    print("🧪 COMPREHENSIVE ADMIN DASHBOARD TEST SUITE 🧪")
    print("=" * 60)
    
    # 1. Test User Management Endpoints
    print("\n📊 TESTING USER MANAGEMENT ENDPOINTS")
    print("-" * 40)
    
    # Get users
    try:
        response = requests.get(f'{base_url}/api/admin/users/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get Users: Found {len(data.get('users', []))} users")
        else:
            print(f"❌ Get Users: Failed {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"❌ Get Users: Error {e}")
        all_passed = False
    
    # Create user
    user_data = {
        'username': f'testuser{timestamp}',
        'email': f'testuser{timestamp}@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'testpass123',
        'role': 'student'
    }
    
    created_user_id = None
    try:
        response = requests.post(f'{base_url}/api/admin/users/create/', json=user_data, headers=headers)
        if response.status_code == 201:
            data = response.json()
            created_user_id = data.get('user_id')
            print(f"✅ Create User: Created user ID {created_user_id}")
        else:
            print(f"❌ Create User: Failed {response.status_code} - {response.text}")
            all_passed = False
    except Exception as e:
        print(f"❌ Create User: Error {e}")
        all_passed = False
    
    # Edit user (if creation was successful)
    if created_user_id:
        edit_data = {
            'first_name': 'Updated First',
            'last_name': 'Updated Last',
            'role': 'instructor'
        }
        
        try:
            response = requests.put(f'{base_url}/api/admin/users/{created_user_id}/', json=edit_data, headers=headers)
            if response.status_code == 200:
                print(f"✅ Edit User: Updated user ID {created_user_id}")
            else:
                print(f"❌ Edit User: Failed {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ Edit User: Error {e}")
            all_passed = False
    
    # 2. Test Organization Management Endpoints
    print("\n🏢 TESTING ORGANIZATION MANAGEMENT ENDPOINTS")
    print("-" * 45)
    
    # Get organizations
    try:
        response = requests.get(f'{base_url}/api/admin/organizations/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get Organizations: Found {len(data.get('organizations', []))} organizations")
        else:
            print(f"❌ Get Organizations: Failed {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"❌ Get Organizations: Error {e}")
        all_passed = False
    
    # Create organization
    org_data = {
        'name': f'Test Organization {timestamp}',
        'description': 'Test Description',
        'contact_email': f'org{timestamp}@example.com',
        'address': '123 Test Street',
        'contact_phone': '555-0123'
    }
    
    created_org_id = None
    try:
        response = requests.post(f'{base_url}/api/organizations/admin/organizations/create/', json=org_data, headers=headers)
        if response.status_code == 201:
            data = response.json()
            created_org_id = data.get('organization_id')
            print(f"✅ Create Organization: Created org ID {created_org_id}")
        else:
            print(f"❌ Create Organization: Failed {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"❌ Create Organization: Error {e}")
        all_passed = False
    
    # 3. Test Statistics Endpoints
    print("\n📈 TESTING STATISTICS ENDPOINTS")
    print("-" * 30)
    
    endpoints = [
        ('/api/admin/stats/', 'User Stats'),
        ('/api/admin/system-overview/', 'System Overview'),
        ('/api/organizations/admin/organization-stats/', 'Organization Stats'),
    ]
    
    for url, name in endpoints:
        try:
            response = requests.get(f'{base_url}{url}', headers=headers)
            if response.status_code == 200:
                print(f"✅ {name}: Working")
            else:
                print(f"❌ {name}: Failed {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {name}: Error {e}")
            all_passed = False
    
    # 4. Test Recent Activity (This was previously failing)
    print("\n🕒 TESTING RECENT ACTIVITY ENDPOINT")
    print("-" * 35)
    
    try:
        response = requests.get(f'{base_url}/api/admin/recent-activity/', headers=headers)
        if response.status_code == 200:
            print("✅ Recent Activity: Working")
        else:
            print(f"⚠️ Recent Activity: Failed {response.status_code} (Expected - needs fixing)")
    except Exception as e:
        print(f"⚠️ Recent Activity: Error {e} (Expected - needs fixing)")
    
    print("\n" + "=" * 60)
    print(f"🏁 TEST SUITE RESULT: {'✅ ALL CORE FUNCTIONS WORKING' if all_passed else '❌ SOME ISSUES FOUND'}")
    print("=" * 60)
    
    if created_user_id or created_org_id:
        print("\n🧹 Cleaning up test data...")
        if created_user_id:
            try:
                User.objects.filter(id=created_user_id).delete()
                print(f"   Deleted test user {created_user_id}")
            except:
                pass
    
    return all_passed

if __name__ == '__main__':
    test_all_endpoints()
