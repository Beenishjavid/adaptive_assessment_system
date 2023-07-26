"""
Debug script to test admin_views import
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_quiz_system.settings')
django.setup()

try:
    print("Testing import...")
    from apps.authentication import admin_views
    print("Import successful!")
    print("Module path:", admin_views.__file__ if hasattr(admin_views, '__file__') else 'No file attribute')
    print("Module dir:", dir(admin_views))
    
    # Check specific function
    if hasattr(admin_views, 'get_all_users'):
        print("get_all_users found!")
    else:
        print("get_all_users NOT found!")
        
    # Try to read the file content
    print("\nReading file content directly...")
    with open('apps/authentication/admin_views.py', 'r') as f:
        content = f.read()
        print(f"File length: {len(content)} characters")
        print(f"Contains 'def get_all_users': {'def get_all_users' in content}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
