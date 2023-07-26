#!/usr/bin/env python
"""
Check and fix admin user credentials and role
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from apps.authentication.models import UserProfile

def check_and_fix_admin():
    """Check and fix admin user setup"""
    print("=== Admin User Setup Check ===")
    
    try:
        # Get admin user
        admin_user = User.objects.get(username='admin')
        print(f"✅ Admin user found: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Is superuser: {admin_user.is_superuser}")
        print(f"   Is staff: {admin_user.is_staff}")
        print(f"   Is active: {admin_user.is_active}")
        
        # Test password
        auth_user = authenticate(username='admin', password='admin123')
        if auth_user:
            print("✅ Password authentication: SUCCESS")
        else:
            print("❌ Password authentication: FAILED")
            admin_user.set_password('admin123')
            admin_user.save()
            print("🔧 Password has been reset to 'admin123'")
            
            # Test again
            auth_user = authenticate(username='admin', password='admin123')
            if auth_user:
                print("✅ Password authentication now works!")
        
        # Check profile
        try:
            profile = admin_user.profile
            print(f"✅ Profile found")
            print(f"   Role: {profile.role}")
            print(f"   Status: {profile.status}")
            
            # Fix role if needed
            if profile.role != 'admin':
                print("🔧 Fixing profile role to 'admin'")
                profile.role = 'admin'
                profile.save()
                print("✅ Profile role updated")
            
            # Ensure active status
            if profile.status != 'active':
                print("🔧 Setting profile status to 'active'")
                profile.status = 'active'
                profile.save()
                print("✅ Profile status updated")
                
        except UserProfile.DoesNotExist:
            print("❌ No profile found for admin user")
            print("🔧 Creating admin profile...")
            profile = UserProfile.objects.create(
                user=admin_user,
                role='admin',
                status='active'
            )
            print("✅ Admin profile created")
        
        return True
        
    except User.DoesNotExist:
        print("❌ Admin user not found!")
        print("🔧 Creating admin user...")
        
        # Create admin user
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@smartquiz.com',
            password='admin123',
            is_superuser=True,
            is_staff=True,
            first_name='Admin',
            last_name='User'
        )
        
        # Create profile (will be created by signal, just update it)
        profile = admin_user.profile
        profile.role = 'admin'
        profile.status = 'active'
        profile.save()
        
        print("✅ Admin user and profile created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login_api():
    """Test the login API with admin credentials"""
    print("\n=== Testing Login API ===")
    
    import requests
    
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = requests.post(
            'http://127.0.0.1:8000/api/auth/login/',
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Login API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"   User ID: {data.get('user', {}).get('id')}")
            print(f"   Username: {data.get('user', {}).get('username')}")
            print(f"   Role: {data.get('user', {}).get('role')}")
            print(f"   Access Token: {data.get('access')[:20]}...")
            
            # This role info should help us debug frontend routing
            return data.get('user', {}).get('role')
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing login API: {e}")
        return None

if __name__ == '__main__':
    admin_fixed = check_and_fix_admin()
    if admin_fixed:
        role = test_login_api()
        print(f"\n=== SUMMARY ===")
        print(f"Admin user setup: {'✅ SUCCESS' if admin_fixed else '❌ FAILED'}")
        print(f"Login test: {'✅ SUCCESS' if role else '❌ FAILED'}")
        if role:
            print(f"Admin role returned: {role}")
            print("The frontend should route to Admin Dashboard for role 'admin'")
    else:
        print("\n❌ Could not set up admin user properly")
