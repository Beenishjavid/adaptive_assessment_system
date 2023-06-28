#!/bin/bash
# Migration Guide for Smart Quiz System

echo "🔄 Django Migration Process"
echo "=========================="

echo "📋 Step 1: Check Current Status"
python manage.py showmigrations

echo "📋 Step 2: Create Migrations for Specific App"
# For quizzes app changes
python manage.py makemigrations quizzes

# For authentication app changes  
python manage.py makemigrations authentication

# For organizations app changes
python manage.py makemigrations organizations

# For all apps
python manage.py makemigrations

echo "📋 Step 3: Review Migration Files"
# Check what migrations were created
ls -la */migrations/

echo "📋 Step 4: Apply Migrations"
python manage.py migrate

echo "📋 Step 5: Verify Migration Status"
python manage.py showmigrations

echo "✅ Migration Complete!"
