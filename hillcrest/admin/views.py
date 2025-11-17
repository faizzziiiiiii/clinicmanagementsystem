from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Department, Employee
from .serializers import (
    DepartmentSerializer,
    EmployeeSerializer,
    AccountInfoSerializer,
    GenerateAccountSerializer,
)

User = get_user_model()


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    Admin can add departments and view/delete them.
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    lookup_field = "id"


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    CRUD for employees.
    - When creating/updating an employee with role=doctor, department is required.
    - Admin can generate login for an employee (creates Django User).
    - Deleting an employee also removes linked user if present.
    """
    queryset = Employee.objects.select_related("department", "user").all()
    serializer_class = EmployeeSerializer
    lookup_field = "id"

    def destroy(self, request, *args, **kwargs):
        """
        Override destroy to delete linked User if exists.
        """
        instance = self.get_object()
        user = getattr(instance, "user", None)
        with transaction.atomic():
            # Remove user first (if you want to keep user, remove this)
            if user:
                user.delete()
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="generate-account")
    def generate_account(self, request, id=None):
        """
        Create a Django User account linked to this employee and return the username & plaintext password.
        Request body can include optional 'username'.
        Endpoint: POST /employees/{id}/generate-account/
        Response: { "username": "...", "password": "..." }
        """
        employee = self.get_object()
        # If already has account, return 400 (or we can recreate)
        if employee.user:
            return Response({"detail": "Account already exists for this employee.", "username": employee.user.username}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GenerateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, plaintext_password = serializer.create_account(employee, serializer.validated_data)
        return Response({"username": user.username, "password": plaintext_password}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="by-role/(?P<role>[^/.]+)")
    def list_by_role(self, request, role=None):
        """
        Optional: list employees by role
        GET /employees/by-role/doctor/
        """
        qs = self.get_queryset().filter(role=role)
        page = self.paginate_queryset(qs)
        if page is not None:
            ser = self.get_serializer(page, many=True)
            return self.get_paginated_response(ser.data)
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View all accounts (Django Users). Admin can see which users are linked to employees.
    This lists users and associated employee details where available.
    """
    queryset = User.objects.select_related("employee_profile").all()
    serializer_class = AccountInfoSerializer
    lookup_field = "id"
