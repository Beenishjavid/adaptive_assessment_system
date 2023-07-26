#!/usr/bin/env python
"""
Insert data into the ACTUAL database tables that exist
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

from django.db import connection
from django.contrib.auth.models import User
import datetime


def insert_real_data():
    print("🔄 Inserting data into ACTUAL database tables...")
    
    # Get or create users
    admin_user = User.objects.get(username='admin')
    instructor_user, created = User.objects.get_or_create(
        username='instructor',
        defaults={
            'email': 'instructor@nstu.com',
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
            'email': 'student@nstu.com',
            'first_name': 'Jane',
            'last_name': 'Student'
        }
    )
    if created:
        student_user.set_password('student123')
        student_user.save()
    
    print(f"✅ Users ready: admin, instructor, student")
    
    with connection.cursor() as cursor:
        # Insert into quizzes_quiz table
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM quizzes_quiz WHERE title = 'Python Programming Basics')
            BEGIN
                INSERT INTO quizzes_quiz (title, description, created_by_id, duration_minutes, passing_score, is_active, quiz_type, created_at, updated_at)
                VALUES ('Python Programming Basics', 'Test your knowledge of Python programming fundamentals', %s, 30, 70, 1, 'assessment', %s, %s)
            END
        """, [instructor_user.id, datetime.datetime.now(), datetime.datetime.now()])
        
        # Get the quiz ID
        cursor.execute("SELECT id FROM quizzes_quiz WHERE title = 'Python Programming Basics'")
        quiz_result = cursor.fetchone()
        if quiz_result:
            quiz_id = quiz_result[0]
            print(f"✅ Quiz created/found: ID {quiz_id}")
            
            # Insert questions
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM quizzes_question WHERE quiz_id = %s AND question_text LIKE 'What is the correct way to define a function%')
                BEGIN
                    INSERT INTO quizzes_question (quiz_id, question_text, question_type, marks, [order], created_at, updated_at)
                    VALUES (%s, 'What is the correct way to define a function in Python?', 'multiple_choice', 5, 1, %s, %s)
                END
            """, [quiz_id, quiz_id, datetime.datetime.now(), datetime.datetime.now()])
            
            # Get question ID
            cursor.execute("SELECT id FROM quizzes_question WHERE quiz_id = %s AND question_text LIKE 'What is the correct way to define a function%'", [quiz_id])
            question_result = cursor.fetchone()
            if question_result:
                question_id = question_result[0]
                
                # Insert choices
                choices = [
                    ('function myFunc():', False, 1),
                    ('def myFunc():', True, 2),
                    ('define myFunc():', False, 3),
                    ('func myFunc():', False, 4)
                ]
                
                for choice_text, is_correct, order in choices:
                    cursor.execute("""
                        IF NOT EXISTS (SELECT 1 FROM quizzes_choice WHERE question_id = %s AND choice_text = %s)
                        BEGIN
                            INSERT INTO quizzes_choice (question_id, choice_text, is_correct, [order])
                            VALUES (%s, %s, %s, %s)
                        END
                    """, [question_id, choice_text, question_id, choice_text, is_correct, order])
            
            # Add second question
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM quizzes_question WHERE quiz_id = %s AND question_text LIKE 'Which of the following is a Python data type%')
                BEGIN
                    INSERT INTO quizzes_question (quiz_id, question_text, question_type, marks, [order], created_at, updated_at)
                    VALUES (%s, 'Which of the following is a Python data type?', 'multiple_choice', 5, 2, %s, %s)
                END
            """, [quiz_id, quiz_id, datetime.datetime.now(), datetime.datetime.now()])
            
            # Get second question ID and add choices
            cursor.execute("SELECT id FROM quizzes_question WHERE quiz_id = %s AND question_text LIKE 'Which of the following is a Python data type%'", [quiz_id])
            question2_result = cursor.fetchone()
            if question2_result:
                question2_id = question2_result[0]
                
                choices2 = [
                    ('list', True, 1),
                    ('array', False, 2),
                    ('vector', False, 3),
                    ('matrix', False, 4)
                ]
                
                for choice_text, is_correct, order in choices2:
                    cursor.execute("""
                        IF NOT EXISTS (SELECT 1 FROM quizzes_choice WHERE question_id = %s AND choice_text = %s)
                        BEGIN
                            INSERT INTO quizzes_choice (question_id, choice_text, is_correct, [order])
                            VALUES (%s, %s, %s, %s)
                        END
                    """, [question2_id, choice_text, question2_id, choice_text, is_correct, order])
        
        # Insert second quiz
        cursor.execute("""
            IF NOT EXISTS (SELECT 1 FROM quizzes_quiz WHERE title = 'Web Development Fundamentals')
            BEGIN
                INSERT INTO quizzes_quiz (title, description, created_by_id, duration_minutes, passing_score, is_active, quiz_type, created_at, updated_at)
                VALUES ('Web Development Fundamentals', 'Basic concepts of web development', %s, 45, 60, 1, 'practice', %s, %s)
            END
        """, [instructor_user.id, datetime.datetime.now(), datetime.datetime.now()])
        
        # Get second quiz ID and add question
        cursor.execute("SELECT id FROM quizzes_quiz WHERE title = 'Web Development Fundamentals'")
        quiz2_result = cursor.fetchone()
        if quiz2_result:
            quiz2_id = quiz2_result[0]
            
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM quizzes_question WHERE quiz_id = %s AND question_text LIKE 'HTML stands for%')
                BEGIN
                    INSERT INTO quizzes_question (quiz_id, question_text, question_type, marks, [order], created_at, updated_at)
                    VALUES (%s, 'HTML stands for:', 'multiple_choice', 4, 1, %s, %s)
                END
            """, [quiz2_id, quiz2_id, datetime.datetime.now(), datetime.datetime.now()])
            
            cursor.execute("SELECT id FROM quizzes_question WHERE quiz_id = %s AND question_text LIKE 'HTML stands for%'", [quiz2_id])
            question3_result = cursor.fetchone()
            if question3_result:
                question3_id = question3_result[0]
                
                choices3 = [
                    ('Hyper Text Markup Language', True, 1),
                    ('High Tech Modern Language', False, 2),
                    ('Home Tool Markup Language', False, 3),
                    ('Hyperlink and Text Markup Language', False, 4)
                ]
                
                for choice_text, is_correct, order in choices3:
                    cursor.execute("""
                        IF NOT EXISTS (SELECT 1 FROM quizzes_choice WHERE question_id = %s AND choice_text = %s)
                        BEGIN
                            INSERT INTO quizzes_choice (question_id, choice_text, is_correct, [order])
                            VALUES (%s, %s, %s, %s)
                        END
                    """, [question3_id, choice_text, question3_id, choice_text, is_correct, order])
        
        # Check final counts
        cursor.execute("SELECT COUNT(*) FROM quizzes_quiz")
        quiz_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM quizzes_question")
        question_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM quizzes_choice")
        choice_count = cursor.fetchone()[0]
        
        print(f"\n🎉 Data inserted successfully!")
        print(f"📊 Final Database Summary:")
        print(f"   Users: {User.objects.count()}")
        print(f"   Quizzes: {quiz_count}")
        print(f"   Questions: {question_count}")
        print(f"   Choices: {choice_count}")
        
        # Display quiz details
        cursor.execute("""
            SELECT q.id, q.title, q.description, q.duration_minutes, 
                   (SELECT COUNT(*) FROM quizzes_question WHERE quiz_id = q.id) as question_count
            FROM quizzes_quiz q
            ORDER BY q.id
        """)
        quizzes = cursor.fetchall()
        print(f"\n🎯 Available Quizzes:")
        for quiz in quizzes:
            print(f"   - ID: {quiz[0]}, Title: {quiz[1]}, Duration: {quiz[3]}min, Questions: {quiz[4]}")


if __name__ == '__main__':
    insert_real_data()
