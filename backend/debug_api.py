#!/usr/bin/env python
"""
Simple API Test to Debug Issues
"""
import os
import sys
import django
import requests
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

from django.contrib.auth.models import User
from apps.authentication.models import UserProfile

# Test URL
BASE_URL = 'http://127.0.0.1:8000'

def test_single_endpoint():
    """Test a single endpoint with detailed error reporting"""
    
    # Get admin user and ensure profile exists
    try:
        admin_user = User.objects.get(username='admin')
        profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={'role': 'admin'}
        )
        print(f"Admin user profile: {profile.role}")
    except Exception as e:
        print(f"Error with admin user: {e}")
        return
    
    # Login to get token
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/login/', json=login_data)
        if response.status_code == 200:
            token = response.json().get('access')
            print("Authentication successful")
        else:
            print(f"Authentication failed: {response.text}")
            return
    except Exception as e:
        print(f"Authentication error: {e}")
        return
    
    # Test admin users endpoint
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(f'{BASE_URL}/api/admin/users/', headers=headers)
        print(f"Admin users endpoint status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response text: {response.text}")
        else:
            data = response.json()
            print(f"Success! Found {len(data.get('users', []))} users")
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == '__main__':
    test_single_endpoint()
