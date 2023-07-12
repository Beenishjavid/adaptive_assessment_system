"""
Organizations Views - Public API endpoints
"""
from rest_framework import generics, permissions
from .models import Organization
from .serializers import OrganizationSerializer


class OrganizationListView(generics.ListAPIView):
    """Public organization list for registration dropdown"""
    queryset = Organization.objects.filter(is_active=True).order_by('name')
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.AllowAny]  # Allow access without authentication
    
    def get_queryset(self):
        """Return only active organizations"""
        return Organization.objects.filter(is_active=True).order_by('name')
