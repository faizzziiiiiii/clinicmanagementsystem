from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    ROLE_DOCTOR = "doctor"
    ROLE_RECEPTIONIST = "receptionist"
    ROLE_PHARMACIST = "pharmacist"
    ROLE_LAB = "lab_technician"

    ROLE_CHOICES = (
        (ROLE_DOCTOR, "Doctor"),
        (ROLE_RECEPTIONIST, "Receptionist"),
        (ROLE_PHARMACIST, "Pharmacist"),
        (ROLE_LAB, "Lab Technician"),
    )

    GENDER_M = "M"
    GENDER_F = "F"
    GENDER_O = "O"
    GENDER_CHOICES = ((GENDER_M, "Male"), (GENDER_F, "Female"), (GENDER_O, "Other"))

    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, blank=True)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=GENDER_O)
    phone = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.SET_NULL, related_name="employees"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # store link to the Django user account created for this employee (optional)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="employee_profile")

    class Meta:
        ordering = ["role", "last_name", "first_name"]

    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return f"{name} ({self.get_role_display()})"
