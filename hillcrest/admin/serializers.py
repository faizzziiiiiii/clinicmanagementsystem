from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Department, Employee
from django.utils.crypto import get_random_string
from django.db import transaction
from django.contrib.auth.hashers import make_password

User = get_user_model()


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]


class EmployeeSerializer(serializers.ModelSerializer):
    # show department as object when reading
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source="department", write_only=True, required=False, allow_null=True
    )

    # show link to user (read-only)
    username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "first_name",
            "last_name",
            "age",
            "gender",
            "phone",
            "role",
            "department",
            "department_id",
            "created_at",
            "updated_at",
            "username",
        ]
        read_only_fields = ["created_at", "updated_at", "username"]

    def get_username(self, obj):
        return obj.user.username if obj.user else None

    def validate(self, attrs):
        """
        Ensure department is provided when role is doctor.
        Note: attrs may contain 'department' if department_id was provided.
        """
        role = attrs.get("role", getattr(self.instance, "role", None))
        # When role is being updated/created, check department presence
        department = attrs.get("department", getattr(self.instance, "department", None))
        if role == Employee.ROLE_DOCTOR and not department:
            raise serializers.ValidationError({"department_id": "Doctor must have a department."})
        return attrs


class AccountInfoSerializer(serializers.ModelSerializer):
    """
    Serializer that lists account info for employees who've got a user.
    """

    employee_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_active", "employee_name", "role", "date_joined"]

    def get_employee_name(self, user):
        e = getattr(user, "employee_profile", None)
        return str(e) if e else None

    def get_role(self, user):
        e = getattr(user, "employee_profile", None)
        return e.role if e else None


class GenerateAccountSerializer(serializers.Serializer):
    """
    Endpoint serializer for generating account for an Employee.
    Returns the generated username and plaintext password (once).
    """
    # optional: allow providing username; else auto-generate
    username = serializers.CharField(required=False, allow_blank=True)
    send_email = serializers.BooleanField(required=False, default=False)  # placeholder, no email sent here

    def create_account(self, employee: Employee, validated_data):
        """
        Creates Django user for the given employee.
        Returns (user, plaintext_password)
        """
        username = validated_data.get("username")
        # generate username if not provided: role + id + first initial + last
        if not username:
            base = (employee.first_name[:1] + (employee.last_name or "")).lower()
            base = "".join(ch for ch in base if ch.isalnum()) or "user"
            username = f"{employee.role[:3]}_{employee.id}_{base}"

        # ensure username uniqueness
        original_username = username
        suffix = 0
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{original_username}{suffix}"

        # generate random password
        password = get_random_string(length=10)
        # create user
        with transaction.atomic():
            user = User.objects.create(
                username=username,
                password=make_password(password),
                is_active=True,
            )
            # link back to employee
            employee.user = user
            employee.save(update_fields=["user"])

        return user, password
