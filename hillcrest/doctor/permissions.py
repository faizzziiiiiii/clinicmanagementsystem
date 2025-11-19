# doctor/permissions.py
from rest_framework.permissions import BasePermission
from admin_panel.models import StaffProfile

class IsDoctor(BasePermission):
    """
    Allow access only to superusers or StaffProfile.role == 'DOCTOR'.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        try:
            sp = StaffProfile.objects.get(user=user)
            return sp.role == 'DOCTOR'
        except StaffProfile.DoesNotExist:
            return False
