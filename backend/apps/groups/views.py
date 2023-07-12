"""
Groups Views - Enhanced group management system
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
import string
import random

from .models import Group, Membership, GroupInvitation, QuizAssignment
from .serializers import (
    GroupSerializer, GroupCreateSerializer, MembershipSerializer, 
    JoinGroupSerializer, UserBasicSerializer, GroupInvitationSerializer,
    QuizAssignmentSerializer, GroupDetailSerializer
)


class GroupListCreateView(generics.ListCreateAPIView):
    """Enhanced group listing and creation with filtering by group type"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GroupCreateSerializer
        return GroupSerializer
    
    def get_queryset(self):
        user = self.request.user
        group_type = self.request.query_params.get('type')
        show_all = self.request.query_params.get('all', '').lower() == 'true'
        
        # Base queryset with proper prefetching
        queryset = Group.objects.select_related('created_by').prefetch_related(
            'memberships__user',
            'quizzes',
            'assigned_quizzes'
        )
        
        # Filter by group type if specified
        if group_type:
            queryset = queryset.filter(group_type=group_type)
        
        # Apply access filters based on user role and request
        if user.userprofile.role == 'admin' and show_all:
            # Admins can see all groups if requested
            pass
        elif user.userprofile.role == 'instructor':
            # Instructors can see their groups, public groups, and course groups
            queryset = queryset.filter(
                Q(created_by=user) |
                Q(memberships__user=user, memberships__is_active=True) |
                Q(is_public=True) |
                Q(group_type='course')
            ).distinct()
        else:
            # Students see their groups and public groups
            queryset = queryset.filter(
                Q(memberships__user=user, memberships__is_active=True) |
                Q(is_public=True)
            ).distinct()
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Enhanced group creation with auto-membership"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create group
        group = serializer.save(created_by=request.user)
        
        # Generate join code if not provided
        if not group.join_code:
            group.generate_join_code()
        
        # Auto-add creator as admin
        Membership.objects.get_or_create(
            group=group,
            user=request.user,
            defaults={'role_in_group': 'admin'}
        )
        
        # Return detailed group info
        response_serializer = GroupDetailSerializer(group, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a specific group"""
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Group.objects.all()
    
    def get_object(self):
        group = super().get_object()
        user = self.request.user
        
        # Check if user has permission to view this group
        if not (group.is_public or 
                group.memberships.filter(user=user, is_active=True).exists() or
                user.is_staff):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to view this group")
        
        return group
    
    def perform_update(self, serializer):
        group = self.get_object()
        user = self.request.user
        
        # Only group admins or creators can update
        membership = group.memberships.filter(user=user, is_active=True).first()
        if not (membership and membership.role_in_group in ['admin', 'instructor'] or
                group.created_by == user or user.is_staff):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to update this group")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        user = self.request.user
        
        # Only group creator or staff can delete
        if not (instance.created_by == user or user.is_staff):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to delete this group")
        
        instance.delete()


class MyGroupsView(generics.ListAPIView):
    """List groups where current user is a member"""
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Group.objects.filter(
            memberships__user=self.request.user,
            memberships__is_active=True
        ).order_by('-created_at')


class PublicGroupsView(generics.ListAPIView):
    """List all public groups"""
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Group.objects.filter(is_public=True, is_active=True).order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def join_group(request):
    """Join a group using join code or group ID"""
    serializer = JoinGroupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    join_code = serializer.validated_data.get('join_code')
    group_id = serializer.validated_data.get('group_id')
    
    # Find the group
    if join_code:
        group = get_object_or_404(Group, join_code=join_code, is_active=True)
    else:
        group = get_object_or_404(Group, id=group_id, is_active=True)
    
    # Check if already a member
    existing_membership = Membership.objects.filter(group=group, user=user).first()
    if existing_membership:
        if existing_membership.is_active:
            return Response(
                {'error': 'You are already a member of this group'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # Reactivate membership
            existing_membership.is_active = True
            existing_membership.save()
            return Response({'message': 'Successfully rejoined the group'})
    
    # Check if group is full
    if group.max_members and group.memberships.filter(is_active=True).count() >= group.max_members:
        return Response(
            {'error': 'Group is full'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create new membership
    membership = Membership.objects.create(
        group=group,
        user=user,
        role_in_group='member'
    )
    
    return Response({
        'message': 'Successfully joined the group',
        'membership': MembershipSerializer(membership).data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def leave_group(request, group_id):
    """Leave a group"""
    group = get_object_or_404(Group, id=group_id)
    user = request.user
    
    membership = get_object_or_404(
        Membership, 
        group=group, 
        user=user, 
        is_active=True
    )
    
    # Check if user is the group creator
    if group.created_by == user:
        return Response(
            {'error': 'Group creator cannot leave the group. Transfer ownership or delete the group instead.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    membership.is_active = False
    membership.save()
    
    return Response({'message': 'Successfully left the group'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_member(request, group_id):
    """Add a member to a group"""
    group = get_object_or_404(Group, id=group_id)
    user = request.user
    
    # Check permissions
    membership = group.memberships.filter(user=user, is_active=True).first()
    if not (membership and membership.role_in_group in ['admin', 'instructor'] or
            group.created_by == user or user.is_staff):
        return Response(
            {'error': 'You don\'t have permission to add members'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    user_id = request.data.get('user_id')
    role = request.data.get('role_in_group', 'member')
    
    if not user_id:
        return Response(
            {'error': 'user_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if already a member
    existing_membership = Membership.objects.filter(group=group, user=target_user).first()
    if existing_membership:
        if existing_membership.is_active:
            return Response(
                {'error': 'User is already a member of this group'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # Reactivate membership
            existing_membership.is_active = True
            existing_membership.role_in_group = role
            existing_membership.save()
            return Response({
                'message': 'User added back to the group',
                'membership': MembershipSerializer(existing_membership).data
            })
    
    # Check if group is full
    if group.max_members and group.memberships.filter(is_active=True).count() >= group.max_members:
        return Response(
            {'error': 'Group is full'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create new membership
    new_membership = Membership.objects.create(
        group=group,
        user=target_user,
        role_in_group=role
    )
    
    return Response({
        'message': 'User added to the group successfully',
        'membership': MembershipSerializer(new_membership).data
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_member(request, group_id, user_id):
    """Remove a member from a group"""
    group = get_object_or_404(Group, id=group_id)
    user = request.user
    
    # Check permissions
    membership = group.memberships.filter(user=user, is_active=True).first()
    if not (membership and membership.role_in_group in ['admin', 'instructor'] or
            group.created_by == user or user.is_staff):
        return Response(
            {'error': 'You don\'t have permission to remove members'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    target_membership = get_object_or_404(
        Membership, 
        group=group, 
        user_id=user_id, 
        is_active=True
    )
    
    # Check if trying to remove group creator
    if group.created_by_id == int(user_id):
        return Response(
            {'error': 'Cannot remove the group creator'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    target_membership.is_active = False
    target_membership.save()
    
    return Response({'message': 'Member removed successfully'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_groups(request):
    """Search groups by name or description"""
    query = request.GET.get('q', '')
    user = request.user
    
    if not query:
        return Response({'results': []})
    
    groups = Group.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True,
        is_public=True
    ).order_by('-created_at')[:20]
    
    serializer = GroupSerializer(groups, many=True, context={'request': request})
    return Response({'results': serializer.data})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_join_code(request, group_id):
    """Generate a new join code for a group"""
    group = get_object_or_404(Group, id=group_id)
    user = request.user
    
    # Check permissions
    membership = group.memberships.filter(user=user, is_active=True).first()
    if not (membership and membership.role_in_group in ['admin', 'instructor'] or
            group.created_by == user or user.is_staff):
        return Response(
            {'error': 'You don\'t have permission to generate join codes'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Generate random join code
    join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Ensure uniqueness
    while Group.objects.filter(join_code=join_code).exists():
        join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    group.join_code = join_code
    group.save()
    
    return Response({'join_code': join_code})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_available_users(request):
    """Get list of users that can be added to groups"""
    query = request.GET.get('q', '')
    
    users = User.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]
    
    serializer = UserBasicSerializer(users, many=True)
    return Response({'users': serializer.data})
