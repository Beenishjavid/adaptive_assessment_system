#!/usr/bin/env python
"""
Simple User Creation Test
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

from django.contrib.auth.models import User
from apps.authentication.models import UserProfile
from django.contrib.auth.hashers import make_password
from django.db import transaction
import time

def test_simple_user_creation():
    """Test simple user creation"""
    timestamp = str(int(time.time()))[-6:]
    
    print("=== Simple User Creation Test ===")
    
    try:
        # Method 1: Without transaction
        print("Testing without transaction...")
        user1 = User.objects.create_user(
            username=f'simpletest{timestamp}',
            email=f'simpletest{timestamp}@example.com',
            password='test123',
            first_name='Simple',
            last_name='Test'
        )
        print(f"Created user {user1.id}: {user1.username}")
        
        # Create profile separately
        profile1 = UserProfile.objects.create(
            user=user1,
            role='student'
        )
        print(f"Created profile {profile1.id} for user {user1.id}")
        
        print("✅ Simple creation successful!")
        return True
        
    except Exception as e:
        print(f"❌ Simple creation failed: {e}")
        return False

def test_transaction_user_creation():
    """Test user creation with transaction"""
    timestamp = str(int(time.time()))[-5:]
    
    print("\n=== Transaction User Creation Test ===")
    
    try:
        with transaction.atomic():
            user2 = User.objects.create_user(
                username=f'txtest{timestamp}',
                email=f'txtest{timestamp}@example.com',
                password='test123',
                first_name='Transaction',
                last_name='Test'
            )
            print(f"Created user {user2.id}: {user2.username}")
            
            profile2 = UserProfile.objects.create(
                user=user2,
                role='instructor'
            )
            print(f"Created profile {profile2.id} for user {user2.id}")
        
        print("✅ Transaction creation successful!")
        return True
        
    except Exception as e:
        print(f"❌ Transaction creation failed: {e}")
        return False

def cleanup_test_users():
    """Clean up test users"""
    print("\n=== Cleanup Test Users ===")
    test_users = User.objects.filter(username__startswith=('simpletest', 'txtest'))
    count = test_users.count()
    if count > 0:
        test_users.delete()
        print(f"Deleted {count} test users")
    else:
        print("No test users to delete")

if __name__ == '__main__':
    # cleanup_test_users()  # Clean up first
    success1 = test_simple_user_creation()
    success2 = test_transaction_user_creation()
    
    print(f"\n=== RESULTS ===")
    print(f"Simple creation: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Transaction creation: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    # cleanup_test_users()  # Clean up after
