from rest_framework import permissions

class IsBookingParticipantOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow:
    - The customer who created the booking
    - The professional assigned to the booking
    - Admins or Dispatchers
    to view or modify it.
    """
    def has_object_permission(self, request, view, obj):
        # Allow superusers, staff, admins, or dispatchers
        if request.user.is_staff or request.user.is_superuser:
            return True
        if request.user.role and request.user.role.name in ['ADMIN', 'SUPER_ADMIN', 'OPERATIONS_MANAGER', 'DISPATCHER']:
            return True
            
        # Allow the customer who created it
        if obj.customer == request.user:
            return True
            
        # Allow the assigned professional
        if obj.assigned_professional and obj.assigned_professional.user == request.user:
            return True
            
        return False
