#!/usr/bin/env python
"""
Final debug attempt - check exact constraint details
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

from django.contrib.auth.models import User
from apps.authentication.models import UserProfile
from django.db import connection
from django.db.models import Max

def check_constraint_details():
    """Check the exact constraint causing issues"""
    print("=== Constraint Investigation ===")
    
    # Get current max IDs
    max_user_id = User.objects.aggregate(max_id=Max('id'))['max_id'] or 0
    max_profile_id = UserProfile.objects.aggregate(max_id=Max('id'))['max_id'] or 0
    
    print(f"Max User ID: {max_user_id}")
    print(f"Max Profile ID: {max_profile_id}")
    
    # Check if there's an issue with the primary key sequence
    try:
        with connection.cursor() as cursor:
            # Check identity info for UserProfile table
            cursor.execute("""
                SELECT 
                    IDENT_CURRENT('users_userprofile') as current_identity,
                    IDENT_INCR('users_userprofile') as increment,
                    IDENT_SEED('users_userprofile') as seed
            """)
            result = cursor.fetchone()
            if result:
                print(f"Identity current: {result[0]}")
                print(f"Identity increment: {result[1]}")
                print(f"Identity seed: {result[2]}")
        
        # Try to reset identity if needed
        print("\n=== Checking if identity reset needed ===")
        if max_profile_id and result and int(result[0]) <= max_profile_id:
            print("Identity column might be out of sync!")
            new_identity = max_profile_id + 1
            print(f"Resetting identity to {new_identity}")
            
            with connection.cursor() as cursor:
                cursor.execute(f"DBCC CHECKIDENT('users_userprofile', RESEED, {new_identity})")
                print("✅ Identity reset successful")
        
    except Exception as e:
        print(f"Error checking identity: {e}")

def try_simple_profile_creation():
    """Try the simplest possible profile creation"""
    print("\n=== Simple Profile Creation Test ===")
    
    try:
        # Find a user that definitely doesn't have a profile
        user_without_profile = None
        for user in User.objects.all():
            if not UserProfile.objects.filter(user=user).exists():
                user_without_profile = user
                break
        
        if user_without_profile:
            print(f"Found user without profile: {user_without_profile.id} - {user_without_profile.username}")
            
            # Create profile the simplest way possible
            profile = UserProfile(user=user_without_profile, role='student')
            profile.save()
            print(f"✅ Successfully created profile {profile.id}")
            return True
        else:
            print("All users already have profiles")
            
            # Create a new user
            test_user = User.objects.create_user(
                username='final_test_user',
                email='final_test@example.com',
                password='test123'
            )
            print(f"Created new user: {test_user.id}")
            
            profile = UserProfile(user=test_user, role='student')
            profile.save()
            print(f"✅ Successfully created profile {profile.id}")
            
            # Clean up
            test_user.delete()
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    check_constraint_details()
    success = try_simple_profile_creation()
    print(f"\nFinal Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
