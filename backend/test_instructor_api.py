#!/usr/bin/env python3
"""
Test script for the new instructor quiz attempts API endpoint
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"
INSTRUCTOR_STATS_URL = f"{BASE_URL}/api/quizzes/api/instructor/stats/"
INSTRUCTOR_ATTEMPTS_URL = f"{BASE_URL}/api/quizzes/api/instructor/quiz-attempts/"

def test_instructor_api():
    """Test the instructor API endpoints"""
    
    # Step 1: Login as instructor
    print("🔐 Logging in as instructor...")
    login_data = {
        "username": "instructor1",
        "password": "instructor123"
    }
    
    session = requests.Session()
    login_response = session.post(LOGIN_URL, json=login_data)
    
    if login_response.status_code == 200:
        login_result = login_response.json()
        print(f"✅ Login successful: {login_result.get('user', {}).get('username', 'instructor')}")
        
        # Set authorization header
        token = login_result.get('access')
        if token:
            session.headers.update({'Authorization': f'Bearer {token}'})
        
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    # Step 2: Test instructor stats endpoint
    print("\n📊 Testing instructor stats endpoint...")
    try:
        stats_response = session.get(INSTRUCTOR_STATS_URL)
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print("✅ Instructor stats retrieved successfully:")
            print(f"   - Total attempts: {stats_data.get('total_attempts', 0)}")
            print(f"   - Average score: {stats_data.get('average_score', 0)}%")
            print(f"   - Active students: {stats_data.get('active_students', 0)}")
            print(f"   - Total quizzes: {stats_data.get('total_quizzes', 0)}")
        else:
            print(f"❌ Stats endpoint failed: {stats_response.status_code}")
            print(f"Response: {stats_response.text}")
    except Exception as e:
        print(f"❌ Error testing stats endpoint: {e}")
    
    # Step 3: Test new instructor quiz attempts endpoint
    print("\n📋 Testing instructor quiz attempts endpoint...")
    try:
        attempts_response = session.get(INSTRUCTOR_ATTEMPTS_URL)
        if attempts_response.status_code == 200:
            attempts_data = attempts_response.json()
            print("✅ Instructor quiz attempts retrieved successfully:")
            
            # Display analytics
            analytics = attempts_data.get('analytics', {})
            print("   Analytics:")
            print(f"   - Total attempts: {analytics.get('total_attempts', 0)}")
            print(f"   - Completed attempts: {analytics.get('completed_attempts', 0)}")
            print(f"   - Total students: {analytics.get('total_students', 0)}")
            print(f"   - Average score: {analytics.get('average_score', 0)}%")
            print(f"   - Completion rate: {analytics.get('completion_rate', 0)}%")
            print(f"   - Quiz count: {analytics.get('quiz_count', 0)}")
            
            # Display quizzes
            quizzes = attempts_data.get('quizzes', [])
            print(f"\n   Quizzes ({len(quizzes)}):")
            for quiz in quizzes[:3]:  # Show first 3 quizzes
                print(f"   - {quiz.get('title', 'N/A')} ({quiz.get('difficulty', 'N/A')}) - {quiz.get('attempt_count', 0)} attempts, avg: {quiz.get('avg_score', 0):.1f}%")
            
            # Display attempts
            attempts = attempts_data.get('attempts', [])
            print(f"\n   Recent Attempts ({len(attempts)}):")
            for attempt in attempts[:5]:  # Show first 5 attempts
                student = attempt.get('student', {})
                quiz = attempt.get('quiz', {})
                print(f"   - {student.get('full_name', 'N/A')} on '{quiz.get('title', 'N/A')}': {attempt.get('score', 'N/A')}% ({attempt.get('status', 'N/A')})")
            
        else:
            print(f"❌ Quiz attempts endpoint failed: {attempts_response.status_code}")
            print(f"Response: {attempts_response.text}")
    except Exception as e:
        print(f"❌ Error testing quiz attempts endpoint: {e}")
    
    # Step 4: Test with quiz filter
    print("\n🎯 Testing quiz attempts endpoint with quiz filter...")
    try:
        # Get first quiz ID if available
        if attempts_data and attempts_data.get('quizzes'):
            first_quiz_id = attempts_data['quizzes'][0]['id']
            filtered_response = session.get(INSTRUCTOR_ATTEMPTS_URL, params={'quiz_id': first_quiz_id})
            
            if filtered_response.status_code == 200:
                filtered_data = filtered_response.json()
                filtered_attempts = filtered_data.get('attempts', [])
                print(f"✅ Filtered results for quiz {first_quiz_id}: {len(filtered_attempts)} attempts")
            else:
                print(f"❌ Filtered endpoint failed: {filtered_response.status_code}")
        else:
            print("ℹ️  No quizzes available to test filtering")
    except Exception as e:
        print(f"❌ Error testing filtered endpoint: {e}")

if __name__ == "__main__":
    print("🧪 Testing Instructor API Endpoints")
    print("=" * 50)
    test_instructor_api()
    print("\n" + "=" * 50)
    print("✅ Test completed!")
