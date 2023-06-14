from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Create sample users for testing'

    def handle(self, *args, **options):
        # Create or update admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'password': make_password('admin123'),
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
                'first_name': 'Admin',
                'last_name': 'User',
                'email': 'admin@example.com',
            }
        )
        
        if not created:
            # Update existing admin user
            admin_user.password = make_password('admin123')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.is_active = True
            admin_user.first_name = 'Admin'
            admin_user.last_name = 'User'
            admin_user.email = 'admin@example.com'
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated admin user: {admin_user.username}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Created admin user: {admin_user.username}')
            )

        # Create admin profile
        admin_profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'admin',
                'status': 'active',
                'phone': '+1234567890',
                'organization': 'Smart Quiz System',
                'bio': 'System Administrator',
            }
        )
        
        if not created:
            admin_profile.role = 'admin'
            admin_profile.status = 'active'
            admin_profile.phone = '+1234567890'
            admin_profile.organization = 'Smart Quiz System'
            admin_profile.bio = 'System Administrator'
            admin_profile.save()

        # Create instructor user
        instructor_user, created = User.objects.get_or_create(
            username='instructor1',
            defaults={
                'password': make_password('instructor123'),
                'is_superuser': False,
                'is_staff': False,
                'is_active': True,
                'first_name': 'John',
                'last_name': 'Instructor',
                'email': 'instructor@example.com',
            }
        )
        
        if not created:
            instructor_user.password = make_password('instructor123')
            instructor_user.save()
            
        self.stdout.write(
            self.style.SUCCESS(f'Created/Updated instructor user: {instructor_user.username}')
        )

        # Create instructor profile
        instructor_profile, created = UserProfile.objects.get_or_create(
            user=instructor_user,
            defaults={
                'role': 'instructor',
                'status': 'active',
                'phone': '+1234567891',
                'organization': 'Education Institute',
                'bio': 'Mathematics Instructor with 10 years of experience.',
                'approved_by': admin_user,
            }
        )

        # Create student users
        students_data = [
            {
                'username': 'student1',
                'password': 'student123',
                'first_name': 'Jane',
                'last_name': 'Student',
                'email': 'student1@example.com',
                'phone': '+1234567892',
                'organization': 'University ABC',
                'bio': 'Computer Science student interested in web development.',
            },
            {
                'username': 'student2',
                'password': 'student123',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'email': 'student2@example.com',
                'phone': '+1234567893',
                'organization': 'College XYZ',
                'bio': 'Business student exploring technology.',
            },
            {
                'username': 'student3',
                'password': 'student123',
                'first_name': 'Sarah',
                'last_name': 'Williams',
                'email': 'student3@example.com',
                'phone': '+1234567894',
                'organization': 'Institute DEF',
                'bio': 'Engineering student passionate about learning.',
            }
        ]

        for student_data in students_data:
            student_user, created = User.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'password': make_password(student_data['password']),
                    'is_superuser': False,
                    'is_staff': False,
                    'is_active': True,
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                    'email': student_data['email'],
                }
            )
            
            if not created:
                student_user.password = make_password(student_data['password'])
                student_user.save()

            # Create student profile
            student_profile, created = UserProfile.objects.get_or_create(
                user=student_user,
                defaults={
                    'role': 'student',
                    'status': 'active',
                    'phone': student_data['phone'],
                    'organization': student_data['organization'],
                    'bio': student_data['bio'],
                    'approved_by': admin_user,
                }
            )

            self.stdout.write(
                self.style.SUCCESS(f'Created/Updated student user: {student_user.username}')
            )

        # Create some pending users for demonstration
        pending_users_data = [
            {
                'username': 'pending_student1',
                'password': 'pending123',
                'first_name': 'Alex',
                'last_name': 'Pending',
                'email': 'pending1@example.com',
                'phone': '+1234567895',
                'organization': 'New Institute',
                'bio': 'New student awaiting approval.',
            },
            {
                'username': 'pending_instructor1',
                'password': 'pending123',
                'first_name': 'Dr. Lisa',
                'last_name': 'Pending',
                'email': 'pending_instructor@example.com',
                'phone': '+1234567896',
                'organization': 'Academic Center',
                'bio': 'Experienced instructor seeking to join the platform.',
            }
        ]

        for pending_data in pending_users_data:
            pending_user, created = User.objects.get_or_create(
                username=pending_data['username'],
                defaults={
                    'password': make_password(pending_data['password']),
                    'is_superuser': False,
                    'is_staff': False,
                    'is_active': True,
                    'first_name': pending_data['first_name'],
                    'last_name': pending_data['last_name'],
                    'email': pending_data['email'],
                }
            )

            # Create pending profile
            role = 'instructor' if 'instructor' in pending_data['username'] else 'student'
            pending_profile, created = UserProfile.objects.get_or_create(
                user=pending_user,
                defaults={
                    'role': role,
                    'status': 'pending',
                    'phone': pending_data['phone'],
                    'organization': pending_data['organization'],
                    'bio': pending_data['bio'],
                }
            )

            self.stdout.write(
                self.style.SUCCESS(f'Created/Updated pending user: {pending_user.username}')
            )

        self.stdout.write(
            self.style.SUCCESS('\n=== Sample Users Created ===')
        )
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Instructor: instructor1 / instructor123')
        self.stdout.write('Students: student1, student2, student3 / student123')
        self.stdout.write('Pending: pending_student1, pending_instructor1 / pending123')
        self.stdout.write(
            self.style.SUCCESS('\nAll users have been created/updated successfully!')
        )
