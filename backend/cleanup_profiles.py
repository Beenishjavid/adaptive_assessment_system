#!/usr/bin/env python
"""
Clean up orphaned UserProfiles
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

from django.contrib.auth.models import User
from apps.authentication.models import UserProfile

def cleanup_orphaned_profiles():
    """Find and clean up orphaned UserProfiles"""
    print("=== Cleaning Up Orphaned Profiles ===")
    
    # Get all user IDs that actually exist
    existing_user_ids = set(User.objects.values_list('id', flat=True))
    print(f"Existing user IDs: {sorted(existing_user_ids)}")
    
    # Get all user IDs referenced by profiles
    profile_user_ids = set(UserProfile.objects.values_list('user_id', flat=True))
    print(f"Profile user IDs: {sorted(profile_user_ids)}")
    
    # Find orphaned profiles (profiles that reference non-existent users)
    orphaned_user_ids = profile_user_ids - existing_user_ids
    print(f"Orphaned profile user IDs: {sorted(orphaned_user_ids)}")
    
    if orphaned_user_ids:
        print(f"Found {len(orphaned_user_ids)} orphaned profiles")
        
        # Show details of orphaned profiles
        orphaned_profiles = UserProfile.objects.filter(user_id__in=orphaned_user_ids)
        for profile in orphaned_profiles:
            print(f"- Profile ID {profile.id}: user_id={profile.user_id}, role={profile.role}")
        
        # Delete orphaned profiles
        deleted_count = orphaned_profiles.delete()[0]
        print(f"✅ Deleted {deleted_count} orphaned profiles")
    else:
        print("✅ No orphaned profiles found")
    
    # Verify cleanup
    print("\n=== After Cleanup ===")
    remaining_user_ids = sorted(User.objects.values_list('id', flat=True))
    remaining_profile_user_ids = sorted(UserProfile.objects.values_list('user_id', flat=True))
    
    print(f"Remaining user IDs: {remaining_user_ids}")
    print(f"Remaining profile user IDs: {remaining_profile_user_ids}")
    
    # Check for mismatches
    if set(remaining_user_ids) == set(remaining_profile_user_ids):
        print("✅ Users and profiles are now in sync")
        return True
    else:
        missing_profiles = set(remaining_user_ids) - set(remaining_profile_user_ids)
        extra_profiles = set(remaining_profile_user_ids) - set(remaining_user_ids)
        if missing_profiles:
            print(f"⚠️ Users without profiles: {sorted(missing_profiles)}")
        if extra_profiles:
            print(f"❌ Still have orphaned profiles: {sorted(extra_profiles)}")
        return False

if __name__ == '__main__':
    cleanup_orphaned_profiles()
