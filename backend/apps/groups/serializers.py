"""
Groups Serializers - Enhanced with full group functionality
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Group, Membership, GroupInvitation, QuizAssignment


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for group members"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class MembershipSerializer(serializers.ModelSerializer):
    """Membership serializer with user details"""
    user = UserBasicSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Membership
        fields = ['id', 'user', 'user_id', 'role_in_group', 'is_active', 'joined_at']


class GroupSerializer(serializers.ModelSerializer):
    """Enhanced group serializer with comprehensive details"""
    created_by = UserBasicSerializer(read_only=True)
    created_by_id = serializers.IntegerField(write_only=True, required=False)
    member_count = serializers.SerializerMethodField()
    quiz_count = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    can_manage = serializers.SerializerMethodField()
    active_assignments = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = [
            'id', 'name', 'description', 'group_type', 'created_by', 'created_by_id',
            'course_code', 'subject', 'is_active', 'is_public', 'max_members',
            'join_code', 'created_at', 'updated_at', 'member_count', 'quiz_count',
            'user_role', 'can_manage', 'active_assignments'
        ]
    
    def get_member_count(self, obj):
        return obj.member_count
    
    def get_quiz_count(self, obj):
        return obj.quiz_count
    
    def get_user_role(self, obj):
        """Get current user's role in the group"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            membership = obj.memberships.filter(user=request.user, is_active=True).first()
            return membership.role_in_group if membership else None
        return None
    
    def get_can_manage(self, obj):
        """Check if current user can manage this group"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if obj.created_by == request.user:
                return True
            membership = obj.memberships.filter(user=request.user, is_active=True).first()
            return membership.can_manage_group() if membership else False
        return False
    
    def get_active_assignments(self, obj):
        """Get count of active assignments"""
        return obj.active_assignments


class GroupDetailSerializer(GroupSerializer):
    """Detailed group serializer with memberships and assignments"""
    memberships = MembershipSerializer(many=True, read_only=True)
    recent_assignments = serializers.SerializerMethodField()
    
    class Meta(GroupSerializer.Meta):
        fields = GroupSerializer.Meta.fields + ['memberships', 'recent_assignments']
    
    def get_recent_assignments(self, obj):
        """Get recent quiz assignments"""
        assignments = obj.assigned_quizzes.select_related('quiz', 'assigned_by').order_by('-assigned_at')[:5]
        return QuizAssignmentSerializer(assignments, many=True).data


class GroupCreateSerializer(serializers.ModelSerializer):
    """Enhanced serializer for group creation"""
    
    class Meta:
        model = Group
        fields = [
            'name', 'description', 'group_type', 'course_code', 
            'subject', 'is_public', 'max_members'
        ]
    
    def validate(self, data):
        """Custom validation based on group type"""
        group_type = data.get('group_type')
        
        # Course groups require course_code for instructors
        if group_type == 'course':
            if not data.get('course_code'):
                raise serializers.ValidationError("Course groups must have a course code")
        
        # Public groups should be accessible
        if group_type == 'public':
            data['is_public'] = True
        
        # Self assessment groups are always private
        if group_type == 'self':
            data['is_public'] = False
            data['max_members'] = 1
        
        return data
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        group = super().create(validated_data)
        
        # Auto-generate join code for certain group types
        if group.group_type in ['course', 'study', 'public']:
            group.generate_join_code()
        
        return group


class GroupInvitationSerializer(serializers.ModelSerializer):
    """Serializer for group invitations"""
    group = GroupSerializer(read_only=True)
    invited_by = UserBasicSerializer(read_only=True)
    invited_user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = GroupInvitation
        fields = [
            'id', 'group', 'invited_by', 'invited_user', 'email',
            'invitation_code', 'status', 'expires_at', 'created_at'
        ]


class QuizAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for quiz assignments"""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    group_name = serializers.CharField(source='group.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    completion_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizAssignment
        fields = [
            'id', 'quiz', 'quiz_title', 'group', 'group_name',
            'assigned_by', 'assigned_by_name', 'due_date', 'is_mandatory',
            'max_attempts_override', 'instructions', 'assigned_at',
            'completion_stats'
        ]
    
    def get_completion_stats(self, obj):
        return obj.completion_stats()


class GroupCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for group creation"""
    
    class Meta:
        model = Group
        fields = [
            'name', 'description', 'group_type', 'course_code', 
            'subject', 'is_public', 'max_members'
        ]
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        group = super().create(validated_data)
        
        # Automatically add creator as admin
        Membership.objects.create(
            group=group,
            user=self.context['request'].user,
            role_in_group='admin'
        )
        
        return group


class JoinGroupSerializer(serializers.Serializer):
    """Enhanced serializer for joining a group"""
    join_code = serializers.CharField(max_length=20, required=False)
    group_id = serializers.IntegerField(required=False)
    invitation_code = serializers.CharField(max_length=50, required=False)
    
    def validate(self, data):
        if not any([data.get('join_code'), data.get('group_id'), data.get('invitation_code')]):
            raise serializers.ValidationError(
                "One of join_code, group_id, or invitation_code is required"
            )
        return data


class GroupSearchSerializer(serializers.Serializer):
    """Serializer for group search functionality"""
    query = serializers.CharField(max_length=200, required=False)
    group_type = serializers.ChoiceField(choices=Group.GROUP_TYPE_CHOICES, required=False)
    topic = serializers.CharField(max_length=100, required=False)
    is_public = serializers.BooleanField(required=False)


class TopicGroupsSerializer(serializers.Serializer):
    """Serializer for finding groups by topic without joining"""
    topic = serializers.CharField(max_length=100)
    include_public = serializers.BooleanField(default=True)
    
    
class BulkInviteSerializer(serializers.Serializer):
    """Serializer for bulk inviting users to a group"""
    emails = serializers.ListField(
        child=serializers.EmailField(),
        max_length=50,
        help_text="List of email addresses to invite"
    )
    message = serializers.CharField(max_length=500, required=False)
    expires_in_days = serializers.IntegerField(default=7, min_value=1, max_value=30)
