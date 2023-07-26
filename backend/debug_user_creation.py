#!/usr/bin/env python
"""
Debug User Creation Issue
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

from django.contrib.auth.models import User
from apps.authentication.models import UserProfile
from django.db import transaction
import time

def debug_user_creation():
    """Debug user creation step by step"""
    print("=== Debug User Creation ===")
    
    # Check current state
    current_users = list(User.objects.values_list('id', flat=True).order_by('id'))
    current_profiles = list(UserProfile.objects.values_list('user_id', flat=True).order_by('user_id'))
    
    print(f"Current users: {current_users}")
    print(f"Current profiles: {current_profiles}")
    
    timestamp = str(int(time.time()))[-6:]
    
    try:
        print("\n--- Step 1: Create User ---")
        user = User(
            username=f'debuguser{timestamp}',
            email=f'debuguser{timestamp}@example.com',
            first_name='Debug',
            last_name='User'
        )
        user.set_password('test123')
        user.save()
        print(f"✅ User created with ID: {user.id}")
        
        print("\n--- Step 2: Check if profile already exists ---")
        existing_profile = UserProfile.objects.filter(user_id=user.id).first()
        if existing_profile:
            print(f"❌ Profile already exists! ID: {existing_profile.id}")
            return False
        else:
            print("✅ No existing profile found")
        
        print("\n--- Step 3: Create Profile ---")
        profile = UserProfile(
            user=user,
            role='student',
            status='active'
        )
        profile.save()
        print(f"✅ Profile created with ID: {profile.id}")
        
        print("\n--- Step 4: Verify ---")
        saved_profile = UserProfile.objects.get(user=user)
        print(f"✅ Profile verified: ID {saved_profile.id}, user_id {saved_profile.user_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in step: {e}")
        # Try to clean up
        try:
            if 'user' in locals():
                user.delete()
                print("Cleaned up user")
        except:
            pass
        return False

def cleanup_debug_users():
    """Clean up debug users"""
    debug_users = User.objects.filter(username__startswith='debuguser')
    count = debug_users.count()
    if count > 0:
        debug_users.delete()
        print(f"Cleaned up {count} debug users")

if __name__ == '__main__':
    cleanup_debug_users()
    success = debug_user_creation()
    print(f"\nResult: {'✅ SUCCESS' if success else '❌ FAILED'}")
    if success:
        cleanup_debug_users()
