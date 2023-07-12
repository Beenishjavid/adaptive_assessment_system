"""
Organizations Serializers - API serialization for organization data
"""
from rest_framework import serializers
from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for organization data"""
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'domain', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
