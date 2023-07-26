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

def test_quiz_update_with_nulls():
    """Test quiz update with null/empty values"""
    
    print("Testing quiz update with null/empty values...")
    
    # Test data with potentially problematic values
    test_cases = [
        {
            "name": "Empty string values",
            "data": {
                "title": "Test Quiz Updated",
                "description": "Test description", 
                "duration_minutes": "",
                "max_attempts": "",
                "passing_score": "",
                "is_active": True
            }
        },
        {
            "name": "Null values",
            "data": {
                "title": "Test Quiz Updated 2",
                "description": "Test description 2", 
                "duration_minutes": None,
                "max_attempts": None,
                "passing_score": None,
                "is_active": True
            }
        },
        {
            "name": "Valid values", 
            "data": {
                "title": "Test Quiz Updated 3",
                "description": "Test description 3", 
                "duration_minutes": 90,
                "max_attempts": 3,
                "passing_score": 75,
                "is_active": True
            }
        }
    ]
    
    # First, login to get a token
    login_data = {
        "username": "instructor1", 
        "password": "instructor123"
    }
    
    try:
        login_response = requests.post(
            'http://127.0.0.1:8000/api/auth/login/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Test each case
            for case in test_cases:
                print(f"\n--- Testing: {case['name']} ---")
                
                response = requests.put(
                    'http://127.0.0.1:8000/api/quizzes/api/quiz/1/update/',
                    json=case['data'],
                    headers=headers
                )
                
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ SUCCESS: Quiz updated successfully")
                    result = response.json()
                    print(f"Response: {result}")
                else:
                    print(f"❌ FAILED: {response.text}")
        
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_quiz_update_with_nulls()
