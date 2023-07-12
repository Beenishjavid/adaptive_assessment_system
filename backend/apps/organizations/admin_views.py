"""
Organization Admin API Views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.organizations.models import Organization
from apps.authentication.models import UserProfile
from django.core.paginator import Paginator
from django.db.models import Q, Count


def check_admin_permission(user):
    """Helper function to check if user has admin permissions"""
    try:
        if user.is_superuser:
            return True
        user_profile = getattr(user, 'profile', None) 
        return user_profile and user_profile.role == 'admin'
    except Exception:
        return False


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_organizations(request):
    """Get all organizations with user counts"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        organizations_query = Organization.objects.all()
        
        if search:
            organizations_query = organizations_query.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        paginator = Paginator(organizations_query, per_page)
        orgs_page = paginator.get_page(page)
        
        organizations_data = []
        for org in orgs_page:
            org_data = {
                'id': org.id,
                'name': org.name,
                'description': org.description,
                'address': org.address,
                'contact_email': org.contact_email,
                'contact_phone': org.phone,  # Fixed field name
                'is_active': org.is_active,
                'created_at': org.created_at.isoformat() if hasattr(org, 'created_at') else None,
                'user_count': org.user_count  # This uses the property method
            }
            organizations_data.append(org_data)
        
        return Response({
            'organizations': organizations_data,
            'total': paginator.count,
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching organizations: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_organization(request):
    """Create a new organization"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        data = request.data
        
        # Check if organization name already exists
        if Organization.objects.filter(name=data.get('name')).exists():
            return Response(
                {'error': 'Organization with this name already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create organization
        organization = Organization.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            address=data.get('address', ''),
            contact_email=data.get('contact_email', ''),
            phone=data.get('contact_phone', ''),  # Fixed field name
            is_active=data.get('is_active', True)
        )
        
        return Response({
            'message': 'Organization created successfully',
            'organization_id': organization.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Error creating organization: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_organization(request, org_id):
    """Update an existing organization"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        organization = get_object_or_404(Organization, id=org_id)
        data = request.data
        
        # Update organization fields
        if 'name' in data and data['name'] != organization.name:
            if Organization.objects.filter(name=data['name']).exists():
                return Response(
                    {'error': 'Organization with this name already exists'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            organization.name = data['name']
        
        if 'description' in data:
            organization.description = data['description']
        if 'address' in data:
            organization.address = data['address']
        if 'contact_email' in data:
            organization.contact_email = data['contact_email']
        if 'contact_phone' in data:
            organization.phone = data['contact_phone']
        if 'is_active' in data:
            organization.is_active = data['is_active']
        
        organization.save()
        
        return Response({
            'message': 'Organization updated successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error updating organization: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_organization(request, org_id):
    """Delete an organization"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        organization = get_object_or_404(Organization, id=org_id)
        
        # Check if organization has users
        user_count = UserProfile.objects.filter(organization=organization).count()
        if user_count > 0:
            return Response(
                {'error': f'Cannot delete organization with {user_count} associated users. Please reassign users first.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        organization.delete()
        
        return Response({
            'message': 'Organization deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error deleting organization: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_stats(request):
    """Get organization statistics for admin dashboard"""
    if not check_admin_permission(request.user):
        return Response(
            {'error': 'Admin access required'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        from datetime import datetime, timedelta
        
        total_organizations = Organization.objects.count()
        active_organizations = Organization.objects.filter(is_active=True).count()
        
        # Recent organizations (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_organizations = Organization.objects.filter(
            created_at__gte=thirty_days_ago
        ).count() if hasattr(Organization, 'created_at') else 0
        
        # Organizations with most users
        top_organizations = Organization.objects.all()[:5]
        
        top_orgs_data = []
        for org in top_organizations:
            top_orgs_data.append({
                'name': org.name,
                'user_count': org.user_count,  # Uses the property method
                'is_active': org.is_active
            })
        
        return Response({
            'total_organizations': total_organizations,
            'active_organizations': active_organizations,
            'recent_organizations': recent_organizations,
            'top_organizations': top_orgs_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Error fetching organization stats: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
