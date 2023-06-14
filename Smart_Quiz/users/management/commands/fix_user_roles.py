from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Fix user roles and profiles'

    def handle(self, *args, **options):
        self.stdout.write('Fixing user roles and profiles...')
        
        # Fix all users without profiles
        users_without_profiles = User.objects.filter(userprofile__isnull=True)
        for user in users_without_profiles:
            if user.is_superuser:
                role = 'admin'
            elif user.is_staff:
                role = 'instructor'
            else:
                role = 'student'
            
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': role}
            )
            
            if created:
                self.stdout.write(f'Created profile for {user.username} with role: {role}')
            else:
                self.stdout.write(f'Profile already exists for {user.username}')
        
        # Fix existing profiles for admin/staff users
        admin_users = User.objects.filter(is_superuser=True)
        for user in admin_users:
            try:
                profile = user.userprofile
                if profile.role != 'admin':
                    profile.role = 'admin'
                    profile.save()
                    self.stdout.write(f'Updated {user.username} role to admin')
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=user, role='admin')
                self.stdout.write(f'Created admin profile for {user.username}')
        
        staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        for user in staff_users:
            try:
                profile = user.userprofile
                if profile.role not in ['admin', 'instructor']:
                    profile.role = 'instructor'
                    profile.save()
                    self.stdout.write(f'Updated {user.username} role to instructor')
            except UserProfile.DoesNotExist:
                UserProfile.objects.create(user=user, role='instructor')
                self.stdout.write(f'Created instructor profile for {user.username}')
        
        self.stdout.write(self.style.SUCCESS('Successfully fixed user roles and profiles!'))
