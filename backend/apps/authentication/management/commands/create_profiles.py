"""
Django management command to create user profiles for existing users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.authentication.models import UserProfile


class Command(BaseCommand):
    help = 'Create UserProfile for existing users who don\'t have one'

    def handle(self, *args, **options):
        self.stdout.write('Checking users without profiles...')
        
        users_without_profiles = []
        for user in User.objects.all():
            try:
                _ = user.profile
            except UserProfile.DoesNotExist:
                users_without_profiles.append(user)
        
        self.stdout.write(f'Found {len(users_without_profiles)} users without profiles')
        
        if users_without_profiles:
            for user in users_without_profiles:
                # Determine role based on user flags
                if user.is_superuser:
                    role = 'admin'
                elif user.is_staff:
                    role = 'instructor'
                else:
                    role = 'student'
                
                # Create profile
                profile = UserProfile.objects.create(
                    user=user,
                    role=role,
                    status='active'
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created profile for {user.username} with role {role}'
                    )
                )
        
        self.stdout.write(self.style.SUCCESS('Profile creation completed!'))
