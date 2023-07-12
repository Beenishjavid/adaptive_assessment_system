"""
API Views for fetching real data from the database
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db import connection
from datetime import datetime
import json


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """Get dashboard statistics from real database"""
    try:
        with connection.cursor() as cursor:
            # Get total quizzes
            cursor.execute("SELECT COUNT(*) FROM Quiz WHERE is_active = 1")
            total_quizzes = cursor.fetchone()[0]
            
            # Get total students
            cursor.execute("SELECT COUNT(*) FROM auth_user WHERE is_active = 1")
            total_students = cursor.fetchone()[0]
            
            # Get total quiz attempts
            cursor.execute("SELECT COUNT(*) FROM QuizAttempt")
            total_attempts = cursor.fetchone()[0]
            
            # Get average score
            cursor.execute("SELECT AVG(CAST(score AS FLOAT)) FROM QuizAttempt")
            avg_score_result = cursor.fetchone()[0]
            avg_score = round(avg_score_result, 1) if avg_score_result else 0
            
            return Response({
                'total_quizzes': total_quizzes,
                'total_students': total_students,
                'total_attempts': total_attempts,
                'average_score': avg_score
            })
    except Exception as e:
        return Response(
            {'error': f'Database error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_quizzes(request):
    """Get all quizzes from database"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT q.quiz_id, q.title, q.description, q.time_limit, 
                       q.total_marks, q.pass_percentage, q.created_at,
                       u.username as created_by_name,
                       (SELECT COUNT(*) FROM Question WHERE quiz_id = q.quiz_id) as question_count
                FROM Quiz q
                LEFT JOIN auth_user u ON q.created_by = u.id
                WHERE q.is_active = 1
                ORDER BY q.created_at DESC
            """)
            
            columns = [col[0] for col in cursor.description]
            quizzes = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Convert datetime objects to ISO format
            for quiz in quizzes:
                if quiz['created_at']:
                    quiz['created_at'] = quiz['created_at'].isoformat()
            
            return Response({'quizzes': quizzes})
    except Exception as e:
        return Response(
            {'error': f'Database error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_quiz_details(request, quiz_id):
    """Get detailed quiz information including questions"""
    try:
        with connection.cursor() as cursor:
            # Get quiz details
            cursor.execute("""
                SELECT q.quiz_id, q.title, q.description, q.time_limit, 
                       q.total_marks, q.pass_percentage, q.created_at,
                       u.username as created_by_name
                FROM Quiz q
                LEFT JOIN auth_user u ON q.created_by = u.id
                WHERE q.quiz_id = %s AND q.is_active = 1
            """, [quiz_id])
            
            quiz_row = cursor.fetchone()
            if not quiz_row:
                return Response(
                    {'error': 'Quiz not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            columns = [col[0] for col in cursor.description]
            quiz = dict(zip(columns, quiz_row))
            
            # Get questions and options
            cursor.execute("""
                SELECT q.question_id, q.question_text, q.question_type, q.marks,
                       o.option_id, o.option_text, o.is_correct
                FROM Question q
                LEFT JOIN [Option] o ON q.question_id = o.question_id
                WHERE q.quiz_id = %s
                ORDER BY q.question_id, o.option_id
            """, [quiz_id])
            
            questions_data = cursor.fetchall()
            questions = {}
            
            for row in questions_data:
                q_id, q_text, q_type, marks, o_id, o_text, is_correct = row
                
                if q_id not in questions:
                    questions[q_id] = {
                        'question_id': q_id,
                        'question_text': q_text,
                        'question_type': q_type,
                        'marks': marks,
                        'options': []
                    }
                
                if o_id:
                    questions[q_id]['options'].append({
                        'option_id': o_id,
                        'option_text': o_text,
                        'is_correct': is_correct
                    })
            
            quiz['questions'] = list(questions.values())
            
            # Convert datetime
            if quiz['created_at']:
                quiz['created_at'] = quiz['created_at'].isoformat()
            
            return Response({'quiz': quiz})
    except Exception as e:
        return Response(
            {'error': f'Database error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_attempts(request):
    """Get recent quiz attempts"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT qa.attempt_id, qa.score, qa.total_questions, qa.time_taken,
                       qa.start_time, qa.end_time, qa.is_passed,
                       u.username, q.title as quiz_title
                FROM QuizAttempt qa
                JOIN auth_user u ON qa.user_id = u.id
                JOIN Quiz q ON qa.quiz_id = q.quiz_id
                ORDER BY qa.start_time DESC
                LIMIT 10
            """)
            
            columns = [col[0] for col in cursor.description]
            attempts = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Convert datetime objects
            for attempt in attempts:
                if attempt['start_time']:
                    attempt['start_time'] = attempt['start_time'].isoformat()
                if attempt['end_time']:
                    attempt['end_time'] = attempt['end_time'].isoformat()
            
            return Response({'attempts': attempts})
    except Exception as e:
        return Response(
            {'error': f'Database error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz_attempt(request):
    """Submit a quiz attempt"""
    try:
        data = request.data
        quiz_id = data.get('quiz_id')
        answers = data.get('answers', [])
        
        if not quiz_id or not answers:
            return Response(
                {'error': 'Missing quiz_id or answers'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with connection.cursor() as cursor:
            # Get quiz details
            cursor.execute("""
                SELECT quiz_id, title, total_marks, pass_percentage
                FROM Quiz WHERE quiz_id = %s
            """, [quiz_id])
            
            quiz = cursor.fetchone()
            if not quiz:
                return Response(
                    {'error': 'Quiz not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate score
            total_score = 0
            total_questions = len(answers)
            
            # Create quiz attempt
            cursor.execute("""
                INSERT INTO QuizAttempt (user_id, quiz_id, score, total_questions, 
                                       time_taken, start_time, end_time, is_passed)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, [
                request.user.id, quiz_id, 0, total_questions, 
                0, datetime.now(), datetime.now(), False
            ])
            
            # Get the attempt ID
            cursor.execute("SELECT SCOPE_IDENTITY()")
            attempt_id = cursor.fetchone()[0]
            
            # Process each answer
            for answer in answers:
                question_id = answer.get('question_id')
                selected_option_id = answer.get('selected_option_id')
                
                # Get correct answer
                cursor.execute("""
                    SELECT o.is_correct, q.marks
                    FROM [Option] o
                    JOIN Question q ON o.question_id = q.question_id
                    WHERE o.option_id = %s
                """, [selected_option_id])
                
                result = cursor.fetchone()
                if result:
                    is_correct, marks = result
                    marks_obtained = marks if is_correct else 0
                    total_score += marks_obtained
                    
                    # Insert user answer
                    cursor.execute("""
                        INSERT INTO UserAnswer (attempt_id, question_id, selected_option_id, 
                                              is_correct, marks_obtained)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [attempt_id, question_id, selected_option_id, is_correct, marks_obtained])
            
            # Update attempt with final score
            percentage = (total_score / quiz[2]) * 100 if quiz[2] > 0 else 0
            is_passed = percentage >= quiz[3]
            
            cursor.execute("""
                UPDATE QuizAttempt 
                SET score = %s, is_passed = %s
                WHERE attempt_id = %s
            """, [total_score, is_passed, attempt_id])
            
            return Response({
                'success': True,
                'attempt_id': attempt_id,
                'score': total_score,
                'total_marks': quiz[2],
                'percentage': round(percentage, 1),
                'is_passed': is_passed
            })
            
    except Exception as e:
        return Response(
            {'error': f'Database error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
