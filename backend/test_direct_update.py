#!/usr/bin/env python3

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

from apps.quizzes.models import Quiz, Question, Choice
from apps.authentication.models import User

def test_update_functionality():
    """Test quiz update functionality directly"""
    
    # Get a test quiz
    quiz = Quiz.objects.first()
    if not quiz:
        print("No quizzes found in database")
        return
    
    print(f"Original quiz status: {quiz.is_active}")
    
    # Test status update
    quiz.is_active = not quiz.is_active
    quiz.save()
    print(f"Updated quiz status: {quiz.is_active}")
    
    # Test question update
    question = quiz.questions.first()
    if question:
        print(f"Original question text: {question.question_text}")
        print(f"Original marks: {question.marks}")
        
        # Update question
        question.question_text = question.question_text + " [UPDATED]"
        question.marks = question.marks + 1
        question.save()
        
        print(f"Updated question text: {question.question_text}")
        print(f"Updated marks: {question.marks}")
        
        # Revert changes
        question.question_text = question.question_text.replace(" [UPDATED]", "")
        question.marks = question.marks - 1
        question.save()
        
        print("Reverted changes")
    
    # Revert quiz status
    quiz.is_active = not quiz.is_active
    quiz.save()
    print(f"Reverted quiz status: {quiz.is_active}")
    
    print("All tests completed successfully!")

if __name__ == "__main__":
    test_update_functionality()
