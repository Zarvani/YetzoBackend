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
        # Allow admins or dispatchers
        if request.user.role and request.user.role.name in ['ADMIN', 'DISPATCHER']:
            return True
            
        # Allow the customer who created it
        if obj.customer == request.user:
            return True
            
        # Allow the assigned professional
        if obj.professional == request.user:
            return True
            
        return False
