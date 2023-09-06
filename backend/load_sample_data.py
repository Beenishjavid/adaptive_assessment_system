#!/usr/bin/env python
"""
Load sample data into the database
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

from django.contrib.auth.models import User
from apps.authentication.models import UserProfile
from apps.organizations.models import Organization
from apps.quizzes.models import Quiz, Question, Choice


def create_sample_data():
    print("Creating sample data...")
    
    # Create organization
    org, created = Organization.objects.get_or_create(
        name="Demo University",
        defaults={
            'description': 'Sample organization for demo',
            'subscription_type': 'premium',
            'is_active': True
        }
    )
    print(f"✅ Organization: {org.name}")
    
    # Create users
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
    
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
    
    print(f"✅ Users created: admin, instructor, student")
    
    # Create user profiles
    UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={
            'organization': org,
            'role': 'admin',
            'full_name': 'Admin User',
            'phone': '+1234567890'
        }
    )
    
    UserProfile.objects.get_or_create(
        user=instructor_user,
        defaults={
            'organization': org,
            'role': 'instructor',
            'full_name': 'John Teacher',
            'phone': '+1234567891'
        }
    )
    
    UserProfile.objects.get_or_create(
        user=student_user,
        defaults={
            'organization': org,
            'role': 'student',
            'full_name': 'Jane Student',
            'phone': '+1234567892'
        }
    )
    
    print(f"✅ User profiles created")
    
    # Create sample quiz
    quiz, created = Quiz.objects.get_or_create(
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
    print(f"✅ Quiz created: {quiz.title}")
    
    # Create sample questions
    q1, created = Question.objects.get_or_create(
        quiz=quiz,
        question_text="What is the correct way to define a function in Python?",
        defaults={
            'question_type': 'multiple_choice',
            'marks': 5,
            'order': 1
        }
    )
    
    if created:
        Choice.objects.create(question=q1, choice_text="function myFunc():", is_correct=False, order=1)
        Choice.objects.create(question=q1, choice_text="def myFunc():", is_correct=True, order=2)
        Choice.objects.create(question=q1, choice_text="define myFunc():", is_correct=False, order=3)
        Choice.objects.create(question=q1, choice_text="func myFunc():", is_correct=False, order=4)
    
    q2, created = Question.objects.get_or_create(
        quiz=quiz,
        question_text="Which of the following is a Python data type?",
        defaults={
            'question_type': 'multiple_choice',
            'marks': 5,
            'order': 2
        }
    )
    
    if created:
        Choice.objects.create(question=q2, choice_text="list", is_correct=True, order=1)
        Choice.objects.create(question=q2, choice_text="array", is_correct=False, order=2)
        Choice.objects.create(question=q2, choice_text="vector", is_correct=False, order=3)
        Choice.objects.create(question=q2, choice_text="matrix", is_correct=False, order=4)
    
    q3, created = Question.objects.get_or_create(
        quiz=quiz,
        question_text="Python is an interpreted language.",
        defaults={
            'question_type': 'true_false',
            'marks': 3,
            'order': 3
        }
    )
    
    if created:
        Choice.objects.create(question=q3, choice_text="True", is_correct=True, order=1)
        Choice.objects.create(question=q3, choice_text="False", is_correct=False, order=2)
    
    print(f"✅ Questions created: {Question.objects.filter(quiz=quiz).count()} questions")
    
    # Create another quiz
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
    
    if created:
        q4, created = Question.objects.get_or_create(
            quiz=quiz2,
            question_text="HTML stands for:",
            defaults={
                'question_type': 'multiple_choice',
                'marks': 4,
                'order': 1
            }
        )
        
        if created:
            Choice.objects.create(question=q4, choice_text="Hyper Text Markup Language", is_correct=True, order=1)
            Choice.objects.create(question=q4, choice_text="High Tech Modern Language", is_correct=False, order=2)
            Choice.objects.create(question=q4, choice_text="Home Tool Markup Language", is_correct=False, order=3)
            Choice.objects.create(question=q4, choice_text="Hyperlink and Text Markup Language", is_correct=False, order=4)
    
    print(f"✅ Second quiz created: {quiz2.title}")
    
    print("\n🎉 Sample data loaded successfully!")
    print("\n📊 Database Summary:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Organizations: {Organization.objects.count()}")
    print(f"   Quizzes: {Quiz.objects.count()}")
    print(f"   Questions: {Question.objects.count()}")
    print(f"   Choices: {Choice.objects.count()}")
    
    print("\n🔐 Login Credentials:")
    print("   Admin: username=admin, password=admin123")
    print("   Instructor: username=instructor, password=instructor123")
    print("   Student: username=student, password=student123")


if __name__ == '__main__':
    create_sample_data()
