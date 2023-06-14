from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from quizzes.models import Quiz, Question, Choice, QuestionBank
from results.models import QuizAttempt, Answer

class Command(BaseCommand):
    help = 'Setup user groups and permissions for the quiz system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up user groups and permissions...')
        
        # Create groups
        admin_group, created = Group.objects.get_or_create(name='Quiz_Admins')
        instructor_group, created = Group.objects.get_or_create(name='Quiz_Instructors')
        student_group, created = Group.objects.get_or_create(name='Quiz_Students')
        
        # Get content types
        quiz_ct = ContentType.objects.get_for_model(Quiz)
        question_ct = ContentType.objects.get_for_model(Question)
        choice_ct = ContentType.objects.get_for_model(Choice)
        questionbank_ct = ContentType.objects.get_for_model(QuestionBank)
        attempt_ct = ContentType.objects.get_for_model(QuizAttempt)
        answer_ct = ContentType.objects.get_for_model(Answer)
        
        # Admin permissions (full access)
        admin_permissions = Permission.objects.filter(
            content_type__in=[quiz_ct, question_ct, choice_ct, questionbank_ct, attempt_ct, answer_ct]
        )
        admin_group.permissions.set(admin_permissions)
        
        # Instructor permissions
        instructor_permissions = []
        
        # Quiz permissions for instructors
        instructor_permissions.extend(Permission.objects.filter(
            content_type=quiz_ct,
            codename__in=['add_quiz', 'change_quiz', 'delete_quiz', 'view_quiz']
        ))
        
        # Question permissions for instructors
        instructor_permissions.extend(Permission.objects.filter(
            content_type=question_ct,
            codename__in=['add_question', 'change_question', 'delete_question', 'view_question']
        ))
        
        # Choice permissions for instructors
        instructor_permissions.extend(Permission.objects.filter(
            content_type=choice_ct,
            codename__in=['add_choice', 'change_choice', 'delete_choice', 'view_choice']
        ))
        
        # Question Bank permissions for instructors
        instructor_permissions.extend(Permission.objects.filter(
            content_type=questionbank_ct,
            codename__in=['add_questionbank', 'change_questionbank', 'delete_questionbank', 'view_questionbank']
        ))
        
        # Quiz Attempt permissions (view and change for grading)
        instructor_permissions.extend(Permission.objects.filter(
            content_type=attempt_ct,
            codename__in=['view_quizattempt', 'change_quizattempt']
        ))
        
        # Answer permissions (view and change for grading)
        instructor_permissions.extend(Permission.objects.filter(
            content_type=answer_ct,
            codename__in=['view_answer', 'change_answer']
        ))
        
        instructor_group.permissions.set(instructor_permissions)
        
        # Student permissions (view only for taking quizzes)
        student_permissions = []
        
        # Students can view quizzes and questions
        student_permissions.extend(Permission.objects.filter(
            content_type=quiz_ct,
            codename='view_quiz'
        ))
        
        student_permissions.extend(Permission.objects.filter(
            content_type=question_ct,
            codename='view_question'
        ))
        
        student_permissions.extend(Permission.objects.filter(
            content_type=choice_ct,
            codename='view_choice'
        ))
        
        # Students can add quiz attempts and answers
        student_permissions.extend(Permission.objects.filter(
            content_type=attempt_ct,
            codename__in=['add_quizattempt', 'view_quizattempt']
        ))
        
        student_permissions.extend(Permission.objects.filter(
            content_type=answer_ct,
            codename__in=['add_answer', 'view_answer']
        ))
        
        student_group.permissions.set(student_permissions)
        
        self.stdout.write(self.style.SUCCESS('Successfully set up user groups and permissions!'))
        self.stdout.write(f'Admin group: {admin_group.permissions.count()} permissions')
        self.stdout.write(f'Instructor group: {instructor_group.permissions.count()} permissions')
        self.stdout.write(f'Student group: {student_group.permissions.count()} permissions')
