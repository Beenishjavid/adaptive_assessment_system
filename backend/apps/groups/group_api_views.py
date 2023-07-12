"""
Enhanced Group API Views - Complete group management system
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import string
import random

from .models import Group, Membership, GroupInvitation, QuizAssignment
from .serializers import (
    GroupSerializer, GroupCreateSerializer, MembershipSerializer, 
    JoinGroupSerializer, UserBasicSerializer, GroupInvitationSerializer,
    QuizAssignmentSerializer, GroupDetailSerializer, GroupSearchSerializer,
    TopicGroupsSerializer, BulkInviteSerializer
)
from apps.quizzes.models import Quiz
from apps.results.models import QuizAttempt
from apps.quizzes.serializers import QuizSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_groups_by_type(request):
    """Get user's groups categorized by type"""
    user = request.user
    
    # Get all user's active memberships
    memberships = Membership.objects.filter(
        user=user, 
        is_active=True
    ).select_related('group', 'group__created_by')
    
    # Categorize groups by type
    groups_by_type = {
        'course': [],
        'study': [],
        'public': [],
        'self': []
    }
    
    for membership in memberships:
        group = membership.group
        group_data = GroupSerializer(group, context={'request': request}).data
        group_data['user_role'] = membership.role_in_group
        groups_by_type[group.group_type].append(group_data)
    
    # Add created groups that user isn't a member of
    created_groups = Group.objects.filter(
        created_by=user,
        is_active=True
    ).exclude(
        id__in=[m.group.id for m in memberships]
    )
    
    for group in created_groups:
        group_data = GroupSerializer(group, context={'request': request}).data
        group_data['user_role'] = 'creator'
        groups_by_type[group.group_type].append(group_data)
    
    return Response({
        'success': True,
        'groups_by_type': groups_by_type,
        'total_groups': sum(len(groups) for groups in groups_by_type.values())
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def discover_public_groups(request):
    """Discover public groups and topic-based groups"""
    query = request.GET.get('query', '')
    topic = request.GET.get('topic', '')
    
    # Base queryset for public groups
    queryset = Group.objects.filter(
        is_public=True,
        is_active=True
    ).exclude(
        # Exclude groups user is already a member of
        memberships__user=request.user,
        memberships__is_active=True
    ).select_related('created_by').prefetch_related('memberships')
    
    # Apply search filters
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(course_code__icontains=query) |
            Q(subject__icontains=query)
        )
    
    if topic:
        queryset = queryset.filter(
            Q(subject__icontains=topic) |
            Q(quizzes__topic__name__icontains=topic)
        ).distinct()
    
    # Serialize results
    groups = GroupSerializer(queryset, many=True, context={'request': request}).data
    
    return Response({
        'success': True,
        'public_groups': groups,
        'count': len(groups)
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_group_enhanced(request):
    """Enhanced group joining with multiple methods"""
    serializer = JoinGroupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    user = request.user
    group = None
    
    try:
        # Find group by different methods
        if data.get('join_code'):
            group = Group.objects.get(join_code=data['join_code'], is_active=True)
        elif data.get('group_id'):
            group = Group.objects.get(id=data['group_id'], is_active=True)
        elif data.get('invitation_code'):
            invitation = GroupInvitation.objects.get(
                invitation_code=data['invitation_code'],
                status='pending'
            )
            if invitation.is_expired():
                return Response({
                    'success': False,
                    'message': 'Invitation has expired'
                }, status=status.HTTP_400_BAD_REQUEST)
            group = invitation.group
        
        if not group:
            return Response({
                'success': False,
                'message': 'Group not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user can join
        can_join, reason = group.can_user_join(user)
        if not can_join:
            return Response({
                'success': False,
                'message': reason
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create membership
        membership, created = Membership.objects.get_or_create(
            group=group,
            user=user,
            defaults={'role_in_group': 'member', 'is_active': True}
        )
        
        if not created:
            # Reactivate if was inactive
            if not membership.is_active:
                membership.is_active = True
                membership.joined_at = timezone.now()
                membership.save()
            else:
                return Response({
                    'success': False,
                    'message': 'Already a member of this group'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update invitation if used
        if data.get('invitation_code'):
            invitation.status = 'accepted'
            invitation.used_at = timezone.now()
            invitation.save()
        
        # Return group details
        group_data = GroupDetailSerializer(group, context={'request': request}).data
        
        return Response({
            'success': True,
            'message': f'Successfully joined {group.name}',
            'group': group_data
        })
        
    except (Group.DoesNotExist, GroupInvitation.DoesNotExist):
        return Response({
            'success': False,
            'message': 'Invalid join code or invitation'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def leave_group_enhanced(request, group_id):
    """Enhanced group leaving with proper cleanup"""
    try:
        group = Group.objects.get(id=group_id, is_active=True)
        membership = Membership.objects.get(group=group, user=request.user, is_active=True)
        
        # Prevent creator from leaving if they're the only admin
        if group.created_by == request.user:
            other_admins = group.memberships.filter(
                role_in_group='admin',
                is_active=True
            ).exclude(user=request.user)
            
            if not other_admins.exists():
                return Response({
                    'success': False,
                    'message': 'Group creator cannot leave without appointing another admin'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Deactivate membership
        membership.is_active = False
        membership.save()
        
        return Response({
            'success': True,
            'message': f'Successfully left {group.name}'
        })
        
    except Group.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Group not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Membership.DoesNotExist:
        return Response({
            'success': False,
            'message': 'You are not a member of this group'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_group_quizzes(request, group_id):
    """Get all quizzes available for a specific group"""
    try:
        group = Group.objects.get(id=group_id)
        
        # Check if user is a member or admin
        if not (group.memberships.filter(user=request.user, is_active=True).exists() or
                request.user.userprofile.role == 'admin'):
            return Response({
                'success': False,
                'message': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get group quizzes and assigned quizzes
        group_quizzes = group.quizzes.filter(is_active=True)
        assigned_quizzes = Quiz.objects.filter(
            group_assignments__group=group,
            is_active=True
        )
        
        all_quizzes = (group_quizzes | assigned_quizzes).distinct()
        
        # Serialize with user attempt info
        quizzes_data = []
        for quiz in all_quizzes:
            quiz_data = QuizSerializer(quiz, context={'request': request}).data
            
            # Add user attempt info
            user_attempts = quiz.get_user_attempts(request.user)
            quiz_data['user_attempts'] = user_attempts.count()
            quiz_data['can_attempt'] = quiz.can_user_attempt(request.user)[0]
            
            # Add assignment info if applicable
            assignment = quiz.group_assignments.filter(group=group).first()
            if assignment:
                quiz_data['assignment'] = QuizAssignmentSerializer(assignment).data
            
            quizzes_data.append(quiz_data)
        
        return Response({
            'success': True,
            'quizzes': quizzes_data,
            'group_name': group.name
        })
        
    except Group.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Group not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_quiz_to_group(request, group_id):
    """Assign a quiz to a group (instructor/admin only)"""
    try:
        group = Group.objects.get(id=group_id, is_active=True)
        
        # Check permissions
        membership = group.memberships.filter(user=request.user, is_active=True).first()
        user_role = getattr(request.user.profile, 'role', 'student') if hasattr(request.user, 'profile') else 'student'
        if not (membership and membership.can_assign_quizzes()) and user_role != 'admin':
            return Response({
                'success': False,
                'message': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        quiz_id = request.data.get('quiz_id')
        quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
        
        # Check if user can assign this quiz
        user_role = getattr(request.user.profile, 'role', 'student') if hasattr(request.user, 'profile') else 'student'
        if quiz.created_by != request.user and user_role != 'admin':
            return Response({
                'success': False,
                'message': 'You can only assign quizzes you created'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create assignment
        assignment, created = QuizAssignment.objects.get_or_create(
            quiz=quiz,
            group=group,
            defaults={
                'assigned_by': request.user,
                'due_date': request.data.get('due_date'),
                'is_mandatory': request.data.get('is_mandatory', True),
                'max_attempts_override': request.data.get('max_attempts_override'),
                'instructions': request.data.get('instructions', '')
            }
        )
        
        if not created:
            return Response({
                'success': False,
                'message': 'Quiz already assigned to this group'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Send notifications to group members
        
        return Response({
            'success': True,
            'message': f'Quiz "{quiz.title}" assigned to group "{group.name}"',
            'assignment': QuizAssignmentSerializer(assignment).data
        })
        
    except Group.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Group not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_quizzes_by_topic(request):
    """Search for quizzes by topic without joining a group"""
    topic = request.GET.get('topic', '')
    if not topic:
        return Response({
            'success': False,
            'message': 'Topic parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find public quizzes by topic
    public_quizzes = Quiz.objects.filter(
        Q(visibility='public') &
        Q(is_active=True) &
        (Q(topic__name__icontains=topic) |
         Q(subject__icontains=topic) |
         Q(description__icontains=topic))
    ).select_related('created_by', 'topic', 'group')
    
    # Find public groups with relevant quizzes
    relevant_groups = Group.objects.filter(
        is_public=True,
        is_active=True,
        quizzes__in=public_quizzes
    ).distinct()
    
    quizzes_data = []
    for quiz in public_quizzes:
        quiz_data = QuizSerializer(quiz, context={'request': request}).data
        can_attempt, reason = quiz.can_user_attempt(request.user)
        quiz_data['can_attempt'] = can_attempt
        quiz_data['attempt_reason'] = reason
        quizzes_data.append(quiz_data)
    
    groups_data = GroupSerializer(relevant_groups, many=True, context={'request': request}).data
    
    return Response({
        'success': True,
        'topic': topic,
        'available_quizzes': quizzes_data,
        'relevant_groups': groups_data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_group_analytics(request, group_id):
    """Get analytics for a group (admin/instructor only)"""
    try:
        group = Group.objects.get(id=group_id)
        
        # Check permissions
        membership = group.memberships.filter(user=request.user, is_active=True).first()
        if not (membership and membership.can_manage_group()) and request.user.userprofile.role != 'admin':
            return Response({
                'success': False,
                'message': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get group statistics
        total_members = group.memberships.filter(is_active=True).count()
        total_quizzes = group.quizzes.filter(is_active=True).count()
        total_assignments = group.assigned_quizzes.count()
        
        # Get quiz completion statistics
        completed_attempts = QuizAttempt.objects.filter(
            quiz__group=group,
            status='completed'
        ).count()
        
        total_possible_attempts = total_members * (total_quizzes + total_assignments)
        completion_rate = (completed_attempts / total_possible_attempts * 100) if total_possible_attempts > 0 else 0
        
        # Get member activity
        member_activity = []
        for membership in group.memberships.filter(is_active=True).select_related('user'):
            user = membership.user
            attempts = QuizAttempt.objects.filter(
                user=user,
                quiz__group=group,
                status='completed'
            ).count()
            
            member_activity.append({
                'user': UserBasicSerializer(user).data,
                'role': membership.role_in_group,
                'completed_quizzes': attempts,
                'joined_at': membership.joined_at
            })
        
        return Response({
            'success': True,
            'analytics': {
                'total_members': total_members,
                'total_quizzes': total_quizzes,
                'total_assignments': total_assignments,
                'completion_rate': round(completion_rate, 2),
                'member_activity': member_activity
            }
        })
        
    except Group.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Group not found'
        }, status=status.HTTP_404_NOT_FOUND)
