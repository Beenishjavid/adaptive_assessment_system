#!/usr/bin/env python
"""
Test database connection and check what data exists
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


def test_database():
    print("🔍 Testing Database Connection and Data...")
    
    # Test Django ORM
    print(f"\n📊 Django ORM Results:")
    print(f"   Total Users: {User.objects.count()}")
    
    # Test direct SQL queries
    print(f"\n📊 Direct SQL Queries:")
    with connection.cursor() as cursor:
        # Check auth_user table
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        user_count = cursor.fetchone()[0]
        print(f"   Users in auth_user: {user_count}")
        
        # Check if Quiz table exists
        try:
            cursor.execute("SELECT COUNT(*) FROM Quiz WHERE is_active = 1")
            quiz_count = cursor.fetchone()[0]
            print(f"   Active Quizzes: {quiz_count}")
        except Exception as e:
            print(f"   Quiz table error: {e}")
        
        # Check if Question table exists
        try:
            cursor.execute("SELECT COUNT(*) FROM Question")
            question_count = cursor.fetchone()[0]
            print(f"   Questions: {question_count}")
        except Exception as e:
            print(f"   Question table error: {e}")
        
        # Check if Users table exists (custom table)
        try:
            cursor.execute("SELECT COUNT(*) FROM Users")
            custom_users = cursor.fetchone()[0]
            print(f"   Users in custom Users table: {custom_users}")
        except Exception as e:
            print(f"   Custom Users table error: {e}")
        
        # List all tables
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
            AND TABLE_CATALOG = 'SmartQuizDB'
            ORDER BY TABLE_NAME
        """)
        tables = cursor.fetchall()
        print(f"\n📋 All Tables in Database:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Check specific quiz data
        try:
            cursor.execute("""
                SELECT quiz_id, title, description, time_limit, created_by 
                FROM Quiz 
                ORDER BY quiz_id
            """)
            quizzes = cursor.fetchall()
            print(f"\n🎯 Quizzes in Database:")
            for quiz in quizzes:
                print(f"   - ID: {quiz[0]}, Title: {quiz[1]}, Time: {quiz[3]}min, Creator: {quiz[4]}")
        except Exception as e:
            print(f"   Quiz query error: {e}")
        
        # Check recent users
        cursor.execute("""
            SELECT id, username, first_name, last_name, email, date_joined
            FROM auth_user 
            ORDER BY date_joined DESC
        """)
        recent_users = cursor.fetchall()
        print(f"\n👥 Recent Users:")
        for user in recent_users[:10]:  # Show last 10 users
            print(f"   - ID: {user[0]}, Username: {user[1]}, Name: {user[2]} {user[3]}, Email: {user[4]}")


if __name__ == '__main__':
    test_database()
