#!/usr/bin/env python
"""
Test Admin CRUD Operations
"""
import os
import sys
import django
import requests
import json

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

def test_organization_creation():
    """Test organization creation endpoint"""
    token = get_admin_token()
    if not token:
        print("❌ Could not get admin token")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test organization creation
    print("=== Testing Organization Creation ===")
    import time
    timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
    data = {
        'name': 'Test Organization ' + timestamp,
        'description': 'Test Description for organization',
        'contact_email': f'test{timestamp}@example.com',
        'address': '123 Test Street',
        'contact_phone': '555-0123'
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/organizations/admin/organizations/create/', 
            json=data,
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Organization creation successful!")
        else:
            print("❌ Organization creation failed!")
            
    except Exception as e:
        print(f"❌ Error testing organization creation: {e}")

def test_user_operations():
    """Test user CRUD operations"""
    token = get_admin_token()
    if not token:
        print("❌ Could not get admin token")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test user creation
    print("\n=== Testing User Creation ===")
    import time
    timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
    user_data = {
        'username': 'testuser' + timestamp,
        'email': f'testuser{timestamp}@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'testpass123',
        'role': 'student'
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/admin/users/create/', 
            json=user_data,
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("✅ User creation successful!")
        else:
            print("❌ User creation failed!")
            
    except Exception as e:
        print(f"❌ Error testing user creation: {e}")
    
    # Test user editing
    print("\n=== Testing User Editing ===")
    edit_data = {
        'first_name': 'Updated First Name',
        'last_name': 'Updated Last Name',
        'role': 'instructor'
    }
    
    try:
        response = requests.put(
            'http://127.0.0.1:8000/api/admin/users/1/', 
            json=edit_data,
            headers=headers
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ User editing successful!")
        else:
            print("❌ User editing failed!")
            
    except Exception as e:
        print(f"❌ Error testing user editing: {e}")

if __name__ == '__main__':
    test_organization_creation()
    test_user_operations()
