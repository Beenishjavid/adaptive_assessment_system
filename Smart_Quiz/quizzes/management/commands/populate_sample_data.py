from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from quizzes.models import Quiz, Question, Choice
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Populate the database with sample quiz data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate sample data...'))
        
        # Create sample users
        instructor_user, created = User.objects.get_or_create(
            username='instructor1',
            defaults={
                'email': 'instructor@example.com',
                'first_name': 'John',
                'last_name': 'Instructor'
            }
        )
        if created:
            instructor_user.set_password('password123')
            instructor_user.save()
            
        # Ensure instructor profile exists
        instructor_profile, created = UserProfile.objects.get_or_create(
            user=instructor_user,
            defaults={'role': 'instructor', 'bio': 'Sample instructor for demonstration'}
        )
        
        student_user, created = User.objects.get_or_create(
            username='student1',
            defaults={
                'email': 'student@example.com',
                'first_name': 'Jane',
                'last_name': 'Student'
            }
        )
        if created:
            student_user.set_password('password123')
            student_user.save()
            
        # Ensure student profile exists
        student_profile, created = UserProfile.objects.get_or_create(
            user=student_user,
            defaults={'role': 'student', 'bio': 'Sample student for demonstration'}
        )
        
        # Create sample quiz
        quiz, created = Quiz.objects.get_or_create(
            title='Python Programming Basics',
            defaults={
                'description': 'Test your knowledge of Python programming fundamentals',
                'created_by': instructor_user,
                'duration_minutes': 30,
                'passing_score': 70,
                'is_active': True,
                'max_attempts': 2
            }
        )
        
        if created:
            # Create questions for the quiz
            q1 = Question.objects.create(
                quiz=quiz,
                question_text='What is the correct way to define a variable in Python?',
                question_type='multiple_choice',
                marks=5,
                order=1
            )
            
            Choice.objects.create(question=q1, choice_text='var x = 10', is_correct=False, order=1)
            Choice.objects.create(question=q1, choice_text='x = 10', is_correct=True, order=2)
            Choice.objects.create(question=q1, choice_text='int x = 10', is_correct=False, order=3)
            Choice.objects.create(question=q1, choice_text='declare x = 10', is_correct=False, order=4)
            
            q2 = Question.objects.create(
                quiz=quiz,
                question_text='Which of the following is a Python data type?',
                question_type='multiple_choice',
                marks=5,
                order=2
            )
            
            Choice.objects.create(question=q2, choice_text='list', is_correct=True, order=1)
            Choice.objects.create(question=q2, choice_text='array', is_correct=False, order=2)
            Choice.objects.create(question=q2, choice_text='vector', is_correct=False, order=3)
            Choice.objects.create(question=q2, choice_text='matrix', is_correct=False, order=4)
            
            q3 = Question.objects.create(
                quiz=quiz,
                question_text='Python is an interpreted language.',
                question_type='true_false',
                marks=3,
                order=3
            )
            
            Choice.objects.create(question=q3, choice_text='True', is_correct=True, order=1)
            Choice.objects.create(question=q3, choice_text='False', is_correct=False, order=2)
            
            q4 = Question.objects.create(
                quiz=quiz,
                question_text='What keyword is used to define a function in Python?',
                question_type='multiple_choice',
                marks=4,
                order=4
            )
            
            Choice.objects.create(question=q4, choice_text='function', is_correct=False, order=1)
            Choice.objects.create(question=q4, choice_text='def', is_correct=True, order=2)
            Choice.objects.create(question=q4, choice_text='func', is_correct=False, order=3)
            Choice.objects.create(question=q4, choice_text='define', is_correct=False, order=4)
        
        # Create another quiz
        quiz2, created = Quiz.objects.get_or_create(
            title='Web Development Fundamentals',
            defaults={
                'description': 'Basic concepts of web development including HTML, CSS, and JavaScript',
                'created_by': instructor_user,
                'duration_minutes': 45,
                'passing_score': 60,
                'is_active': True,
                'max_attempts': 3
            }
        )
        
        if created:
            q1 = Question.objects.create(
                quiz=quiz2,
                question_text='What does HTML stand for?',
                question_type='multiple_choice',
                marks=3,
                order=1
            )
            
            Choice.objects.create(question=q1, choice_text='Hyper Text Markup Language', is_correct=True, order=1)
            Choice.objects.create(question=q1, choice_text='High Tech Modern Language', is_correct=False, order=2)
            Choice.objects.create(question=q1, choice_text='Home Tool Markup Language', is_correct=False, order=3)
            Choice.objects.create(question=q1, choice_text='Hyperlink and Text Markup Language', is_correct=False, order=4)
            
            q2 = Question.objects.create(
                quiz=quiz2,
                question_text='CSS is used for styling web pages.',
                question_type='true_false',
                marks=2,
                order=2
            )
            
            Choice.objects.create(question=q2, choice_text='True', is_correct=True, order=1)
            Choice.objects.create(question=q2, choice_text='False', is_correct=False, order=2)
        
        self.stdout.write(
            self.style.SUCCESS(
                'Successfully populated sample data!\n'
                'Sample accounts created:\n'
                '- Instructor: username=instructor1, password=password123\n'
                '- Student: username=student1, password=password123\n'
                'Sample quizzes created:\n'
                '- Python Programming Basics\n'
                '- Web Development Fundamentals'
            )
        )
