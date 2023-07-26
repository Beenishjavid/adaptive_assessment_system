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

from apps.quizzes.models import Quiz, Question, Choice
from apps.authentication.models import User

def test_quiz_update_api():
    """Test the quiz update API endpoint"""
    
    # Get a test quiz
    quiz = Quiz.objects.first()
    if not quiz:
        print("No quizzes found in database")
        return
    
    print(f"Testing quiz update for quiz ID: {quiz.id}")
    print(f"Quiz title: {quiz.title}")
    print(f"Current status: {quiz.is_active}")
    
    # Test 1: Status-only update
    print("\n--- Test 1: Status-only update ---")
    status_update_data = {
        "is_active": not quiz.is_active
    }
    
    try:
        response = requests.put(
            f'http://127.0.0.1:8000/api/quizzes/api/quiz/{quiz.id}/update/',
            json=status_update_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status update response: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 401:
            print("Authentication required - this is expected")
        
    except Exception as e:
        print(f"Status update error: {e}")
    
    # Test 2: Check question structure
    print("\n--- Test 2: Question data structure ---")
    questions = quiz.questions.all()[:2]  # Get first 2 questions
    
    for q in questions:
        print(f"Question ID: {q.id}")
        print(f"Question text: {q.question_text}")
        print(f"Question type: {q.question_type}")
        print(f"Marks: {q.marks}")
        
        choices = q.choices.all()
        for c in choices:
            print(f"  Choice: {c.choice_text} (correct: {c.is_correct})")
        print()
    
    # Test 3: Full update data structure
    print("\n--- Test 3: Full update data structure ---")
    full_update_data = {
        "title": quiz.title,
        "description": quiz.description,
        "duration_minutes": quiz.duration_minutes,
        "max_attempts": quiz.max_attempts,
        "passing_score": quiz.passing_score,
        "quiz_type": quiz.quiz_type,
        "visibility": quiz.visibility,
        "randomize_questions": quiz.randomize_questions,
        "allow_review": quiz.allow_review,
        "is_active": quiz.is_active,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "marks": q.marks,
                "choices": [
                    {
                        "id": c.id,
                        "choice_text": c.choice_text,
                        "is_correct": c.is_correct
                    } for c in q.choices.all()
                ]
            } for q in questions
        ]
    }
    
    print(f"Full update data structure:")
    print(json.dumps(full_update_data, indent=2)[:500] + "...")

if __name__ == "__main__":
    test_quiz_update_api()
