"""
Django management command to load sample quiz data
Usage: python manage.py load_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from apps.authentication.models import UserProfile
from apps.groups.models import Group, Membership
from apps.quizzes.models import Topic, Quiz, Question, Choice


class Command(BaseCommand):
    help = 'Load sample data for testing the Smart Quiz System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading sample data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Loading sample data...')
        
        # Create sample users
        users = self.create_sample_users()
        
        # Create sample topics
        topics = self.create_sample_topics()
        
        # Create sample groups
        groups = self.create_sample_groups(users)
        
        # Create sample quizzes with questions
        quizzes = self.create_sample_quizzes(users, topics, groups)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded sample data:\n'
                f'- {len(users)} users\n'
                f'- {len(topics)} topics\n'
                f'- {len(groups)} groups\n'
                f'- {len(quizzes)} quizzes\n'
            )
        )

    def clear_data(self):
        """Clear existing data"""
        Choice.objects.all().delete()
        Question.objects.all().delete()
        Quiz.objects.all().delete()
        Topic.objects.all().delete()
        Membership.objects.all().delete()
        Group.objects.all().delete()
        UserProfile.objects.filter(user__username__in=['instructor1', 'instructor2', 'student1', 'student2', 'student3']).delete()
        User.objects.filter(username__in=['instructor1', 'instructor2', 'student1', 'student2', 'student3']).delete()

    def create_sample_users(self):
        """Create sample users with profiles"""
        users_data = [
            {
                'username': 'instructor1',
                'email': 'instructor1@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'instructor',
                'password': 'instructor123'
            },
            {
                'username': 'instructor2',
                'email': 'instructor2@example.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'instructor',
                'password': 'instructor123'
            },
            {
                'username': 'student1',
                'email': 'student1@example.com',
                'first_name': 'Alice',
                'last_name': 'Brown',
                'role': 'student',
                'password': 'student123'
            },
            {
                'username': 'student2',
                'email': 'student2@example.com',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'role': 'student',
                'password': 'student123'
            },
            {
                'username': 'student3',
                'email': 'student3@example.com',
                'first_name': 'Carol',
                'last_name': 'Davis',
                'role': 'student',
                'password': 'student123'
            }
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_active': True,
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                
                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    role=user_data['role'],
                    status='active',
                    phone=f'+1-555-{random.randint(1000, 9999)}',
                    bio=f"Sample {user_data['role']} for testing",
                    organization='Sample University'
                )
                
            users.append(user)
            
        return users

    def create_sample_topics(self):
        """Create sample quiz topics"""
        topics_data = [
            {'name': 'Mathematics', 'description': 'Mathematical concepts and problems'},
            {'name': 'Computer Science', 'description': 'Programming and computer science fundamentals'},
            {'name': 'Physics', 'description': 'Physics principles and applications'},
            {'name': 'Chemistry', 'description': 'Chemical reactions and molecular science'},
            {'name': 'History', 'description': 'Historical events and analysis'},
        ]

        topics = []
        for topic_data in topics_data:
            topic, created = Topic.objects.get_or_create(
                name=topic_data['name'],
                defaults=topic_data
            )
            topics.append(topic)

        return topics

    def create_sample_groups(self, users):
        """Create sample groups"""
        instructors = [u for u in users if hasattr(u, 'userprofile') and u.userprofile.role == 'instructor']
        students = [u for u in users if hasattr(u, 'userprofile') and u.userprofile.role == 'student']

        groups_data = [
            {
                'name': 'CS 101 - Introduction to Programming',
                'description': 'Basic programming concepts and Python fundamentals',
                'group_type': 'course',
                'course_code': 'CS101',
                'subject': 'Computer Science',
                'created_by': instructors[0] if instructors else users[0],
                'is_public': False,
            },
            {
                'name': 'Math Study Group',
                'description': 'Collaborative mathematics problem solving',
                'group_type': 'study',
                'subject': 'Mathematics',
                'created_by': instructors[1] if len(instructors) > 1 else users[0],
                'is_public': True,
            },
            {
                'name': 'Physics Lab Session',
                'description': 'Physics laboratory experiments and discussions',
                'group_type': 'course',
                'course_code': 'PHYS201',
                'subject': 'Physics',
                'created_by': instructors[0] if instructors else users[0],
                'is_public': False,
            }
        ]

        groups = []
        for group_data in groups_data:
            group, created = Group.objects.get_or_create(
                name=group_data['name'],
                defaults=group_data
            )
            
            if created:
                # Add creator as admin
                Membership.objects.create(
                    group=group,
                    user=group_data['created_by'],
                    role_in_group='admin'
                )
                
                # Add some students as members
                for student in students[:2]:  # Add first 2 students to each group
                    Membership.objects.get_or_create(
                        group=group,
                        user=student,
                        defaults={'role_in_group': 'member'}
                    )
                    
            groups.append(group)

        return groups

    def create_sample_quizzes(self, users, topics, groups):
        """Create sample quizzes with questions and choices"""
        instructors = [u for u in users if hasattr(u, 'userprofile') and u.userprofile.role == 'instructor']
        
        quizzes_data = [
            {
                'title': 'Python Basics Quiz',
                'description': 'Test your knowledge of Python programming fundamentals',
                'topic': next((t for t in topics if t.name == 'Computer Science'), None),
                'group': groups[0] if groups else None,
                'quiz_type': 'assessment',
                'duration_minutes': 30,
                'questions': [
                    {
                        'text': 'What is the correct way to define a function in Python?',
                        'type': 'multiple_choice',
                        'choices': [
                            {'text': 'def function_name():', 'correct': True},
                            {'text': 'function function_name():', 'correct': False},
                            {'text': 'define function_name():', 'correct': False},
                            {'text': 'func function_name():', 'correct': False},
                        ]
                    },
                    {
                        'text': 'Python is an interpreted language.',
                        'type': 'true_false',
                        'choices': [
                            {'text': 'True', 'correct': True},
                            {'text': 'False', 'correct': False},
                        ]
                    },
                    {
                        'text': 'Which of the following is used to create a list in Python?',
                        'type': 'multiple_choice',
                        'choices': [
                            {'text': '[]', 'correct': True},
                            {'text': '{}', 'correct': False},
                            {'text': '()', 'correct': False},
                            {'text': '<>', 'correct': False},
                        ]
                    }
                ]
            },
            {
                'title': 'Basic Mathematics Quiz',
                'description': 'Test your basic mathematical skills',
                'topic': next((t for t in topics if t.name == 'Mathematics'), None),
                'group': groups[1] if len(groups) > 1 else None,
                'quiz_type': 'practice',
                'duration_minutes': 45,
                'questions': [
                    {
                        'text': 'What is 15 + 27?',
                        'type': 'multiple_choice',
                        'choices': [
                            {'text': '42', 'correct': True},
                            {'text': '41', 'correct': False},
                            {'text': '43', 'correct': False},
                            {'text': '40', 'correct': False},
                        ]
                    },
                    {
                        'text': 'The square root of 64 is 8.',
                        'type': 'true_false',
                        'choices': [
                            {'text': 'True', 'correct': True},
                            {'text': 'False', 'correct': False},
                        ]
                    }
                ]
            },
            {
                'title': 'Physics Fundamentals',
                'description': 'Basic physics concepts and principles',
                'topic': next((t for t in topics if t.name == 'Physics'), None),
                'group': groups[2] if len(groups) > 2 else None,
                'quiz_type': 'assessment',
                'duration_minutes': 60,
                'questions': [
                    {
                        'text': 'What is the unit of force in the SI system?',
                        'type': 'multiple_choice',
                        'choices': [
                            {'text': 'Newton', 'correct': True},
                            {'text': 'Joule', 'correct': False},
                            {'text': 'Watt', 'correct': False},
                            {'text': 'Pascal', 'correct': False},
                        ]
                    },
                    {
                        'text': 'Light travels faster than sound.',
                        'type': 'true_false',
                        'choices': [
                            {'text': 'True', 'correct': True},
                            {'text': 'False', 'correct': False},
                        ]
                    }
                ]
            }
        ]

        quizzes = []
        for quiz_data in quizzes_data:
            quiz, created = Quiz.objects.get_or_create(
                title=quiz_data['title'],
                defaults={
                    'description': quiz_data['description'],
                    'created_by': instructors[0] if instructors else users[0],
                    'topic': quiz_data['topic'],
                    'group': quiz_data['group'],
                    'quiz_type': quiz_data['quiz_type'],
                    'duration_minutes': quiz_data['duration_minutes'],
                    'visibility': 'group' if quiz_data['group'] else 'public',
                    'start_time': timezone.now(),
                    'end_time': timezone.now() + timedelta(days=30),
                }
            )
            
            if created:
                # Create questions for this quiz
                for i, question_data in enumerate(quiz_data['questions'], 1):
                    question = Question.objects.create(
                        quiz=quiz,
                        question_text=question_data['text'],
                        question_type=question_data['type'],
                        marks=1,
                        order=i
                    )
                    
                    # Create choices for this question
                    for j, choice_data in enumerate(question_data['choices'], 1):
                        Choice.objects.create(
                            question=question,
                            choice_text=choice_data['text'],
                            is_correct=choice_data['correct'],
                            order=j
                        )
                        
            quizzes.append(quiz)

        return quizzes
