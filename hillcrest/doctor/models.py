from django.db import models
from admin_panel.models import StaffProfile, BillingRecord
from receptionist.models import Appointment, Patient


class Prescription(models.Model):
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='prescription'
    )

    doctor = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    notes = models.TextField(null=True, blank=True)
    diagnosis = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 NEW FIELD: pharmacist will update this
    is_dispensed = models.BooleanField(default=False)

    def __str__(self):
        return f"Prescription {self.id} for appt {self.appointment_id}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items'
    )

    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.medicine_name} ({self.prescription_id})"


class LabOrder(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    doctor = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    tests = models.JSONField()  # e.g. [{"test": "CBC", "price": 100}]
    created_at = models.DateTimeField(auto_now_add=True)

    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"LabOrder {self.id} for appt {self.appointment_id}"


class PharmacyOrder(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    doctor = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    items = models.JSONField()  # e.g. [{"name": "Paracetamol", "qty": 2, "price": 20}]
    created_at = models.DateTimeField(auto_now_add=True)

    is_dispensed = models.BooleanField(default=False)

    def __str__(self):
        return f"PharmacyOrder {self.id} for appt {self.appointment_id}"
