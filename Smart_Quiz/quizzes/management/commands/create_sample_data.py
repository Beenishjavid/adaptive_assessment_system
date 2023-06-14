from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from quizzes.models import Quiz, Question, Choice
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Create sample data for demo'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create instructor user
        instructor, created = User.objects.get_or_create(
            username='instructor1',
            defaults={
                'email': 'instructor@example.com',
                'first_name': 'John',
                'last_name': 'Teacher',
                'is_staff': False
            }
        )
        if created:
            instructor.set_password('password123')
            instructor.save()
            UserProfile.objects.create(user=instructor, role='instructor')
            self.stdout.write(f'Created instructor: {instructor.username}')

        # Create student user
        student, created = User.objects.get_or_create(
            username='student1',
            defaults={
                'email': 'student@example.com',
                'first_name': 'Jane',
                'last_name': 'Student',
                'is_staff': False
            }
        )
        if created:
            student.set_password('password123')
            student.save()
            UserProfile.objects.create(user=student, role='student')
            self.stdout.write(f'Created student: {student.username}')

        # Create sample quiz
        quiz, created = Quiz.objects.get_or_create(
            title='Python Programming Basics',
            defaults={
                'description': 'Test your knowledge of Python programming fundamentals including variables, data types, and basic syntax.',
                'instructor': instructor,
                'duration_minutes': 15,
                'total_marks': 20,
                'pass_marks': 12,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created quiz: {quiz.title}')

            # Question 1
            q1 = Question.objects.create(
                quiz=quiz,
                question_text='What is the correct way to declare a variable in Python?',
                question_type='mcq',
                marks=5,
                order=1
            )
            Choice.objects.create(question=q1, choice_text='var x = 10', is_correct=False, order=1)
            Choice.objects.create(question=q1, choice_text='x = 10', is_correct=True, order=2)
            Choice.objects.create(question=q1, choice_text='int x = 10', is_correct=False, order=3)
            Choice.objects.create(question=q1, choice_text='declare x = 10', is_correct=False, order=4)

            # Question 2
            q2 = Question.objects.create(
                quiz=quiz,
                question_text='Which of the following is a Python data type?',
                question_type='mcq',
                marks=5,
                order=2
            )
            Choice.objects.create(question=q2, choice_text='string', is_correct=True, order=1)
            Choice.objects.create(question=q2, choice_text='array', is_correct=False, order=2)
            Choice.objects.create(question=q2, choice_text='char', is_correct=False, order=3)
            Choice.objects.create(question=q2, choice_text='float64', is_correct=False, order=4)

            # Question 3
            q3 = Question.objects.create(
                quiz=quiz,
                question_text='Python is case-sensitive.',
                question_type='true_false',
                marks=5,
                order=3
            )
            Choice.objects.create(question=q3, choice_text='True', is_correct=True, order=1)
            Choice.objects.create(question=q3, choice_text='False', is_correct=False, order=2)

            # Question 4
            q4 = Question.objects.create(
                quiz=quiz,
                question_text='What does "print()" function do in Python?',
                question_type='mcq',
                marks=5,
                order=4
            )
            Choice.objects.create(question=q4, choice_text='Prints to printer', is_correct=False, order=1)
            Choice.objects.create(question=q4, choice_text='Displays output on screen', is_correct=True, order=2)
            Choice.objects.create(question=q4, choice_text='Saves to file', is_correct=False, order=3)
            Choice.objects.create(question=q4, choice_text='Creates a copy', is_correct=False, order=4)

        # Create another quiz
        quiz2, created = Quiz.objects.get_or_create(
            title='Web Development Fundamentals',
            defaults={
                'description': 'Basic concepts of web development including HTML, CSS, and JavaScript.',
                'instructor': instructor,
                'duration_minutes': 20,
                'total_marks': 15,
                'pass_marks': 9,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created quiz: {quiz2.title}')

            # Question 1
            q1 = Question.objects.create(
                quiz=quiz2,
                question_text='What does HTML stand for?',
                question_type='mcq',
                marks=5,
                order=1
            )
            Choice.objects.create(question=q1, choice_text='Hyper Text Markup Language', is_correct=True, order=1)
            Choice.objects.create(question=q1, choice_text='Home Tool Markup Language', is_correct=False, order=2)
            Choice.objects.create(question=q1, choice_text='Hyperlinks Text Mark Language', is_correct=False, order=3)
            Choice.objects.create(question=q1, choice_text='Hyper Text Making Language', is_correct=False, order=4)

            # Question 2
            q2 = Question.objects.create(
                quiz=quiz2,
                question_text='CSS is used for styling web pages.',
                question_type='true_false',
                marks=5,
                order=2
            )
            Choice.objects.create(question=q2, choice_text='True', is_correct=True, order=1)
            Choice.objects.create(question=q2, choice_text='False', is_correct=False, order=2)

            # Question 3
            q3 = Question.objects.create(
                quiz=quiz2,
                question_text='Which language is used for web page behavior?',
                question_type='mcq',
                marks=5,
                order=3
            )
            Choice.objects.create(question=q3, choice_text='HTML', is_correct=False, order=1)
            Choice.objects.create(question=q3, choice_text='CSS', is_correct=False, order=2)
            Choice.objects.create(question=q3, choice_text='JavaScript', is_correct=True, order=3)
            Choice.objects.create(question=q3, choice_text='Python', is_correct=False, order=4)

        # Update quiz total marks
        for quiz in Quiz.objects.all():
            total = sum(q.marks for q in quiz.questions.all())
            quiz.total_marks = total
            quiz.save()

        self.stdout.write(
            self.style.SUCCESS('Sample data created successfully!')
        )
        self.stdout.write('Demo accounts:')
        self.stdout.write('- Instructor: instructor1 / password123')
        self.stdout.write('- Student: student1 / password123')
