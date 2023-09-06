#!/usr/bin/env python
"""
Simple data insertion using Django ORM with correct table names
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

from django.contrib.auth.models import User
from apps.quizzes.models import Quiz, Question, Choice
from apps.authentication.models import UserProfile
from apps.organizations.models import Organization


def create_sample_data_orm():
    print("🔄 Creating sample data using Django ORM...")
    
    # Create organization if it doesn't exist
    org, created = Organization.objects.get_or_create(
        name="Demo University",
        defaults={
            'description': 'Noakhali Science and Technology University',
            'subscription_type': 'premium',
            'is_active': True
        }
    )
    print(f"✅ Organization: {org.name}")
    
    # Get existing users or create them
    admin_user = User.objects.get(username='admin')
    
    instructor_user, created = User.objects.get_or_create(
        username='instructor',
        defaults={
            'email': 'instructor@example.com',
            'first_name': 'John',
            'last_name': 'Teacher'
        }
    )
    if created:
        instructor_user.set_password('instructor123')
        instructor_user.save()
    
    student_user, created = User.objects.get_or_create(
        username='student',
        defaults={
            'email': 'student@example.com',
            'first_name': 'Jane',
            'last_name': 'Student'
        }
    )
    if created:
        student_user.set_password('student123')
        student_user.save()
    
    print(f"✅ Users: admin, instructor, student")
    
    # Create user profiles
    UserProfile.objects.get_or_create(
        user=instructor_user,
        defaults={
            'organization': org,
            'role': 'instructor',
            'full_name': 'John Teacher',
            'phone': '+8801700000001'
        }
    )
    
    UserProfile.objects.get_or_create(
        user=student_user,
        defaults={
            'organization': org,
            'role': 'student',
            'full_name': 'Jane Student',
            'phone': '+8801700000002'
        }
    )
    
    print(f"✅ User profiles created")
    
    # Create quiz using the Quiz model (which maps to quizzes_quiz table)
    quiz1, created = Quiz.objects.get_or_create(
        title="Python Programming Basics",
        defaults={
            'description': 'Test your knowledge of Python programming fundamentals',
            'created_by': instructor_user,
            'duration_minutes': 30,
            'passing_score': 70,
            'is_active': True,
            'quiz_type': 'assessment'
        }
    )
    print(f"✅ Quiz 1: {quiz1.title} (ID: {quiz1.id})")
    
    if created:
        # Question 1
        q1 = Question.objects.create(
            quiz=quiz1,
            question_text="What is the correct way to define a function in Python?",
            question_type='multiple_choice',
            marks=5,
            order=1
        )
        
        Choice.objects.create(question=q1, choice_text="function myFunc():", is_correct=False, order=1)
        Choice.objects.create(question=q1, choice_text="def myFunc():", is_correct=True, order=2)
        Choice.objects.create(question=q1, choice_text="define myFunc():", is_correct=False, order=3)
        Choice.objects.create(question=q1, choice_text="func myFunc():", is_correct=False, order=4)
        
        # Question 2
        q2 = Question.objects.create(
            quiz=quiz1,
            question_text="Which of the following is a Python data type?",
            question_type='multiple_choice',
            marks=5,
            order=2
        )
        
        Choice.objects.create(question=q2, choice_text="list", is_correct=True, order=1)
        Choice.objects.create(question=q2, choice_text="array", is_correct=False, order=2)
        Choice.objects.create(question=q2, choice_text="vector", is_correct=False, order=3)
        Choice.objects.create(question=q2, choice_text="matrix", is_correct=False, order=4)
        
        # Question 3
        q3 = Question.objects.create(
            quiz=quiz1,
            question_text="Python is an interpreted language.",
            question_type='true_false',
            marks=3,
            order=3
        )
        
        Choice.objects.create(question=q3, choice_text="True", is_correct=True, order=1)
        Choice.objects.create(question=q3, choice_text="False", is_correct=False, order=2)
        
        print(f"✅ Questions created for Quiz 1")
    
    # Create second quiz
    quiz2, created = Quiz.objects.get_or_create(
        title="Web Development Fundamentals",
        defaults={
            'description': 'Basic concepts of web development',
            'created_by': instructor_user,
            'duration_minutes': 45,
            'passing_score': 60,
            'is_active': True,
            'quiz_type': 'practice'
        }
    )
    print(f"✅ Quiz 2: {quiz2.title} (ID: {quiz2.id})")
    
    if created:
        # Question for quiz 2
        q4 = Question.objects.create(
            quiz=quiz2,
            question_text="HTML stands for:",
            question_type='multiple_choice',
            marks=4,
            order=1
        )
        
        Choice.objects.create(question=q4, choice_text="Hyper Text Markup Language", is_correct=True, order=1)
        Choice.objects.create(question=q4, choice_text="High Tech Modern Language", is_correct=False, order=2)
        Choice.objects.create(question=q4, choice_text="Home Tool Markup Language", is_correct=False, order=3)
        Choice.objects.create(question=q4, choice_text="Hyperlink and Text Markup Language", is_correct=False, order=4)
        
        # Add more web dev questions
        q5 = Question.objects.create(
            quiz=quiz2,
            question_text="CSS is used for:",
            question_type='multiple_choice',
            marks=4,
            order=2
        )
        
        Choice.objects.create(question=q5, choice_text="Styling web pages", is_correct=True, order=1)
        Choice.objects.create(question=q5, choice_text="Database operations", is_correct=False, order=2)
        Choice.objects.create(question=q5, choice_text="Server configuration", is_correct=False, order=3)
        Choice.objects.create(question=q5, choice_text="Network protocols", is_correct=False, order=4)
        
        print(f"✅ Questions created for Quiz 2")
    
    # Final summary
    total_quizzes = Quiz.objects.count()
    total_questions = Question.objects.count()
    total_choices = Choice.objects.count()
    total_users = User.objects.count()
    
    print(f"\n🎉 Sample data created successfully!")
    print(f"📊 Database Summary:")
    print(f"   Users: {total_users}")
    print(f"   Organizations: {Organization.objects.count()}")
    print(f"   Quizzes: {total_quizzes}")
    print(f"   Questions: {total_questions}")
    print(f"   Choices: {total_choices}")
    
    print(f"\n🎯 Available Quizzes:")
    for quiz in Quiz.objects.all():
        question_count = quiz.questions.count()
        print(f"   - {quiz.title} ({question_count} questions, {quiz.duration_minutes}min)")
    
    print(f"\n🔐 Login Credentials:")
    print(f"   Admin: username=admin, password=admin123")
    print(f"   Instructor: username=instructor, password=instructor123")
    print(f"   Student: username=student, password=student123")


if __name__ == '__main__':
    create_sample_data_orm()
