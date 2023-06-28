@echo off
echo 🔄 Django Migration Process for Windows
echo ==========================================

echo.
echo 📋 Step 1: Activate Virtual Environment
call "D:\Project\Web_Eng\.venv\Scripts\activate.bat"

echo.
echo 📋 Step 2: Navigate to Backend Directory
cd "D:\Project\Web_Eng\backend"

echo.
echo 📋 Step 3: Check Current Migration Status
python manage.py showmigrations

echo.
echo 📋 Step 4: Create New Migrations (if any changes detected)
python manage.py makemigrations

echo.
echo 📋 Step 5: Create Migrations for Specific Apps
python manage.py makemigrations authentication
python manage.py makemigrations organizations  
python manage.py makemigrations quizzes
python manage.py makemigrations groups
python manage.py makemigrations results
python manage.py makemigrations proctoring
python manage.py makemigrations notifications

echo.
echo 📋 Step 6: Apply All Migrations
python manage.py migrate

echo.
echo 📋 Step 7: Verify Final Status
python manage.py showmigrations

echo.
echo ✅ Migration Process Complete!
echo.
pause
