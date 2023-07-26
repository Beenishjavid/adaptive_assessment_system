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

from apps.authentication.models import User

def test_authentication():
    """Test authentication flow"""
    
    # Check available users
    users = User.objects.all()
    print("Available users:")
    for user in users:
        print(f"- Username: {user.username}, Email: {user.email}")
    
    # Try to login as instructor1
    login_data = {
        "username": "instructor1",
        "password": "instructor123"  # Try common password
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:8000/api/auth/login/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"\nLogin attempt 1 - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            # Try with different password
            login_data["password"] = "password123"
            response = requests.post(
                'http://127.0.0.1:8000/api/auth/login/',
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            print(f"\nLogin attempt 2 - Status: {response.status_code}")
            print(f"Response: {response.text}")
            
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access')
            
            # Test authenticated request
            print(f"\nTesting authenticated request with token...")
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test quiz update
            update_response = requests.put(
                'http://127.0.0.1:8000/api/quizzes/api/quiz/1/update/',
                json={"is_active": True},
                headers=headers
            )
            
            print(f"Quiz update - Status: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            
    except Exception as e:
        print(f"Authentication test error: {e}")

if __name__ == "__main__":
    test_authentication()
