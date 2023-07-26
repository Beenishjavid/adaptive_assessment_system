#!/usr/bin/env python
"""
Comprehensive cleanup and fix for UserProfile constraints
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

def comprehensive_cleanup():
    """Complete cleanup of user/profile mismatches"""
    print("=== Comprehensive Cleanup ===")
    
    # Get all users and profiles
    all_users = list(User.objects.values('id', 'username'))
    all_profiles = list(UserProfile.objects.values('id', 'user_id', 'role'))
    
    print(f"Total users: {len(all_users)}")
    print(f"Total profiles: {len(all_profiles)}")
    
    # Find and delete orphaned profiles
    existing_user_ids = {u['id'] for u in all_users}
    
    orphaned_profiles = []
    for profile in all_profiles:
        if profile['user_id'] not in existing_user_ids:
            orphaned_profiles.append(profile)
    
    if orphaned_profiles:
        print(f"\nFound {len(orphaned_profiles)} orphaned profiles:")
        for profile in orphaned_profiles:
            print(f"- Profile ID {profile['id']}: user_id={profile['user_id']}, role={profile['role']}")
        
        # Delete orphaned profiles
        orphaned_ids = [p['id'] for p in orphaned_profiles]
        deleted = UserProfile.objects.filter(id__in=orphaned_ids).delete()[0]
        print(f"✅ Deleted {deleted} orphaned profiles")
    
    # Find users without profiles
    profile_user_ids = {p['user_id'] for p in all_profiles if p['user_id'] in existing_user_ids}
    users_without_profiles = []
    
    for user in all_users:
        if user['id'] not in profile_user_ids:
            users_without_profiles.append(user)
    
    if users_without_profiles:
        print(f"\nFound {len(users_without_profiles)} users without profiles:")
        for user in users_without_profiles:
            print(f"- User ID {user['id']}: {user['username']}")
            # Create missing profiles
            try:
                UserProfile.objects.create(
                    user_id=user['id'],
                    role='student',
                    status='active'
                )
                print(f"  ✅ Created profile for user {user['id']}")
            except Exception as e:
                print(f"  ❌ Failed to create profile for user {user['id']}: {e}")
    
    print("\n=== Final State ===")
    final_users = User.objects.count()
    final_profiles = UserProfile.objects.count()
    print(f"Users: {final_users}")
    print(f"Profiles: {final_profiles}")
    
    if final_users == final_profiles:
        print("✅ Users and profiles are now perfectly synchronized!")
        return True
    else:
        print(f"❌ Still have mismatch: {final_users} users vs {final_profiles} profiles")
        return False

def test_new_user_creation():
    """Test creating a completely new user"""
    print("\n=== Testing New User Creation ===")
    
    import time
    timestamp = str(int(time.time()))[-6:]
    
    try:
        with transaction.atomic():
            # Create user first
            user = User.objects.create_user(
                username=f'cleantest{timestamp}',
                email=f'cleantest{timestamp}@example.com',
                password='test123',
                first_name='Clean',
                last_name='Test'
            )
            print(f"✅ Created user: {user.id} - {user.username}")
            
            # Create profile
            profile = UserProfile.objects.create(
                user=user,
                role='student',
                status='active'
            )
            print(f"✅ Created profile: {profile.id} for user {user.id}")
        
        # Verify
        saved_profile = UserProfile.objects.get(user=user)
        print(f"✅ Verified: Profile {saved_profile.id} exists for user {user.id}")
        
        # Clean up test user
        user.delete()
        print(f"✅ Cleaned up test user")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    # Step 1: Cleanup
    cleanup_success = comprehensive_cleanup()
    
    if cleanup_success:
        # Step 2: Test new user creation
        test_success = test_new_user_creation()
        print(f"\nFinal Result: {'✅ ALL WORKING' if test_success else '❌ STILL ISSUES'}")
    else:
        print("\n❌ Cleanup failed - cannot proceed to testing")
