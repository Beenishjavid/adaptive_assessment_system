from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import UserProfile

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
import json
import csv
from .models import UserProfile

def logout_view(request):
    """Custom logout view that handles both GET and POST requests"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

class CustomUserCreationForm(UserCreationForm):
    """Custom registration form with additional fields"""
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email required
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
        # Add CSS classes
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

def register(request):
    """Enhanced user registration view with role selection"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        role = request.POST.get('role', 'student')
        phone = request.POST.get('phone', '')
        organization = request.POST.get('organization', '')
        bio = request.POST.get('bio', '')
        
        if form.is_valid():
            user = form.save()
            
            # Update user profile with additional information
            profile = user.userprofile
            profile.role = role
            profile.phone = phone
            profile.organization = organization
            profile.bio = bio
            
            # Set status based on role
            if role == 'instructor':
                profile.status = 'pending'  # Instructors need approval
                messages.warning(request, 
                    f'Account created for {user.username}! Your instructor account is pending approval. '
                    'You will receive an email once approved.')
            else:  # student
                profile.status = 'active'
                profile.approved_at = timezone.now()
                messages.success(request, f'Account created for {user.username}! You can now log in.')
            
            profile.save()
            
            # Auto-login active users
            if profile.status == 'active':
                login(request, user)
                return redirect('home')
            else:
                return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'title': 'Register - Smart Quiz'
    }
    return render(request, 'users/register.html', context)

@login_required
def profile(request):
    """User profile view"""
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        user_profile = UserProfile.objects.create(user=request.user, role='student')
    
    if request.method == 'POST':
        # Update profile
        bio = request.POST.get('bio', '')
        user_profile.bio = bio
        user_profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'user_profile': user_profile,
        'title': 'My Profile'
    }
    return render(request, 'users/profile.html', context)

@login_required
def dashboard(request):
    """User dashboard"""
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        # Create profile based on user type
        if user.is_superuser:
            profile = UserProfile.objects.create(user=user, role='admin')
        elif user.is_staff:
            profile = UserProfile.objects.create(user=user, role='instructor')
        else:
            profile = UserProfile.objects.create(user=user, role='student')
    
    context = {
        'user': user,
        'profile': profile,
        'title': 'Dashboard'
    }
    
    # Redirect to role-specific dashboard
    if profile.role == 'admin' or user.is_superuser:
        return redirect('admin_dashboard')
    elif profile.role == 'instructor':
        return redirect('instructor_dashboard')
    else:
        return redirect('student_dashboard')

@login_required
def instructor_dashboard(request):
    """Instructor dashboard"""
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, role='instructor')
    
    # Check if user is instructor
    if profile.role != 'instructor' and not user.is_superuser:
        messages.error(request, 'Access denied. Instructor privileges required.')
        return redirect('home')
    
    from quizzes.models import Quiz
    from results.models import QuizAttempt
    
    # Instructor statistics
    user_quizzes = Quiz.objects.filter(created_by=user)
    total_quizzes = user_quizzes.count()
    total_attempts = QuizAttempt.objects.filter(quiz__created_by=user).count()
    
    context = {
        'user': user,
        'profile': profile,
        'total_quizzes': total_quizzes,
        'total_attempts': total_attempts,
        'recent_quizzes': user_quizzes.order_by('-created_at')[:5],
        'title': 'Instructor Dashboard'
    }
    return render(request, 'users/instructor_dashboard.html', context)

@login_required
def student_dashboard(request):
    """Student dashboard"""
    user = request.user
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, role='student')
    
    from results.models import QuizAttempt
    from quizzes.models import Quiz
    
    # Student statistics
    user_attempts = QuizAttempt.objects.filter(user=user)
    total_attempts = user_attempts.count()
    completed_attempts = user_attempts.filter(status='completed').count()
    available_quizzes = Quiz.objects.filter(is_active=True).count()
    
    context = {
        'user': user,
        'profile': profile,
        'total_attempts': total_attempts,
        'completed_attempts': completed_attempts,
        'available_quizzes': available_quizzes,
        'recent_attempts': user_attempts.order_by('-started_at')[:5],
        'title': 'Student Dashboard'
    }
    return render(request, 'users/student_dashboard.html', context)

def is_admin(user):
    """Check if user is admin"""
    if user.is_superuser:
        return True
    try:
        return user.userprofile.role == 'admin'
    except UserProfile.DoesNotExist:
        return False

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard for user management"""
    # Get filter parameter
    status_filter = request.GET.get('status', 'all')
    
    # Statistics
    stats = {
        'total_users': User.objects.count(),
        'pending_approvals': UserProfile.objects.filter(status='pending').count(),
        'active_instructors': UserProfile.objects.filter(role='instructor', status='active').count(),
        'students': UserProfile.objects.filter(role='student').count(),
    }
    
    # Pending instructor approvals
    pending_instructors = UserProfile.objects.filter(
        role='instructor', 
        status='pending'
    ).select_related('user').order_by('-user__date_joined')
    
    # All user profiles with filtering
    user_profiles_query = UserProfile.objects.select_related('user').order_by('-user__date_joined')
    
    if status_filter != 'all':
        user_profiles_query = user_profiles_query.filter(status=status_filter)
    
    user_profiles = user_profiles_query[:50]  # Limit to 50 for performance
    
    context = {
        'stats': stats,
        'pending_instructors': pending_instructors,
        'user_profiles': user_profiles,
        'status_filter': status_filter,
        'title': 'Admin Dashboard'
    }
    
    return render(request, 'users/admin_dashboard.html', context)

@user_passes_test(is_admin)
@require_http_methods(["POST"])
def approve_user(request, profile_id):
    """Approve a pending user"""
    try:
        profile = get_object_or_404(UserProfile, id=profile_id)
        
        if profile.status != 'pending':
            return JsonResponse({
                'success': False, 
                'message': 'User is not pending approval'
            })
        
        profile.status = 'active'
        profile.approved_by = request.user
        profile.approved_at = timezone.now()
        profile.save()
        
        # Assign to appropriate group
        profile.assign_to_group()
        
        messages.success(request, f'User {profile.user.username} has been approved!')
        
        return JsonResponse({
            'success': True, 
            'message': f'User {profile.user.username} approved successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': str(e)
        })

@user_passes_test(is_admin)
@require_http_methods(["POST"])
def reject_user(request, profile_id):
    """Reject a pending user"""
    try:
        profile = get_object_or_404(UserProfile, id=profile_id)
        
        profile.status = 'rejected'
        profile.save()
        
        messages.success(request, f'User {profile.user.username} has been rejected!')
        
        return JsonResponse({
            'success': True, 
            'message': f'User {profile.user.username} rejected successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': str(e)
        })

@user_passes_test(is_admin)
def view_profile_detail(request, profile_id):
    """View detailed profile information"""
    profile = get_object_or_404(UserProfile, id=profile_id)
    
    context = {
        'profile': profile,
    }
    
    return render(request, 'users/profile_detail.html', context)

@user_passes_test(is_admin)
def export_users(request):
    """Export users to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Username', 'First Name', 'Last Name', 'Email', 'Role', 
        'Status', 'Date Joined', 'Last Login', 'Organization', 'Phone'
    ])
    
    for profile in UserProfile.objects.select_related('user').all():
        writer.writerow([
            profile.user.username,
            profile.user.first_name,
            profile.user.last_name,
            profile.user.email,
            profile.get_role_display(),
            profile.get_status_display(),
            profile.user.date_joined.strftime('%Y-%m-%d') if profile.user.date_joined else '',
            profile.user.last_login.strftime('%Y-%m-%d') if profile.user.last_login else '',
            profile.organization or '',
            profile.phone or '',
        ])
    
    return response

@user_passes_test(is_admin)
def edit_user(request, profile_id):
    """Edit user profile (admin only)"""
    profile = get_object_or_404(UserProfile, id=profile_id)
    
    if request.method == 'POST':
        # Update user basic info
        user = profile.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # Update profile info
        profile.role = request.POST.get('role', profile.role)
        profile.status = request.POST.get('status', profile.status)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.organization = request.POST.get('organization', profile.organization)
        profile.bio = request.POST.get('bio', profile.bio)
        profile.save()
        
        # Update groups based on role
        profile.assign_to_group()
        
        messages.success(request, f'User {user.username} updated successfully!')
        return redirect('admin_dashboard')
    
    context = {
        'profile': profile,
        'title': f'Edit User - {profile.user.username}'
    }
    
    return render(request, 'users/edit_user.html', context)

@user_passes_test(is_admin)
@require_http_methods(["DELETE"])
def delete_user(request, profile_id):
    """Delete a user (admin only)"""
    try:
        profile = get_object_or_404(UserProfile, id=profile_id)
        user = profile.user
        username = user.username
        
        # Don't allow deletion of current admin
        if user == request.user:
            return JsonResponse({
                'success': False, 
                'message': 'Cannot delete your own account'
            })
        
        # Don't allow deletion of superusers unless requester is superuser
        if user.is_superuser and not request.user.is_superuser:
            return JsonResponse({
                'success': False, 
                'message': 'Cannot delete superuser accounts'
            })
        
        user.delete()  # This will also delete the profile due to CASCADE
        
        return JsonResponse({
            'success': True, 
            'message': f'User {username} deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': str(e)
        })
