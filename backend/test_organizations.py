#!/usr/bin/env python
"""
Test Organizations Admin API
"""
import os
import sys
import django
import requests

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

def test_organizations_endpoints():
    """Test all organizations endpoints"""
    token = get_admin_token()
    if not token:
        print("❌ Could not get admin token")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    base_url = 'http://127.0.0.1:8000'
    
    # Test main organizations endpoint that was failing
    print("--- Testing Organizations Admin Endpoint ---")
    try:
        response = requests.get(f'{base_url}/api/organizations/admin/organizations/', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Found {len(data.get('organizations', []))} organizations")
            print(f"Total: {data.get('total', 'N/A')}")
        else:
            print(f"❌ FAILED: {response.text[:200]}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test organization stats
    print("\n--- Testing Organization Stats ---")
    try:
        response = requests.get(f'{base_url}/api/organizations/admin/organization-stats/', headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Total orgs: {data.get('total_organizations', 'N/A')}")
            print(f"Active orgs: {data.get('active_organizations', 'N/A')}")
        else:
            print(f"❌ FAILED: {response.text[:200]}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == '__main__':
    test_organizations_endpoints()
