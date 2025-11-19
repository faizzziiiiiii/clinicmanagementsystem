# doctor/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from admin_panel.models import StaffProfile, BillingRecord
from receptionist.models import Appointment
from .models import Prescription, PrescriptionItem, LabOrder, PharmacyOrder
from .serializers import (
    PrescriptionSerializer,
    PrescriptionItemSerializer,
    LabOrderSerializer,
    PharmacyOrderSerializer
)
from .permissions import IsDoctor


# --------------------------------------------------------------
# LIST APPOINTMENTS FOR LOGGED-IN DOCTOR
# --------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDoctor])
def my_appointments(request):
    doctor = StaffProfile.objects.get(user=request.user)
    appts = Appointment.objects.filter(doctor=doctor).order_by("-appointment_datetime")

    from receptionist.serializers import AppointmentSerializer
    return Response(AppointmentSerializer(appts, many=True).data)


# --------------------------------------------------------------
# APPOINTMENT DETAIL
# --------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDoctor])
def appointment_detail(request, appt_id):
    doctor = StaffProfile.objects.get(user=request.user)

    try:
        appt = Appointment.objects.get(id=appt_id, doctor=doctor)
    except Appointment.DoesNotExist:
        return Response({"detail": "Appointment not found or not assigned to you"}, status=404)

    from receptionist.serializers import AppointmentSerializer
    return Response(AppointmentSerializer(appt).data)


# --------------------------------------------------------------
# CREATE PRESCRIPTION (BASE)
# --------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDoctor])
def create_prescription(request, appt_id):
    doctor = StaffProfile.objects.get(user=request.user)

    try:
        appt = Appointment.objects.get(id=appt_id, doctor=doctor)
    except Appointment.DoesNotExist:
        return Response({"detail": "Appointment not found or not assigned to you"}, status=404)

    data = request.data.copy()
    data["appointment"] = appt.id
    data["patient"] = appt.patient.id
    data["doctor"] = doctor.id

    serializer = PrescriptionSerializer(data=data)
    if serializer.is_valid():
        pres = serializer.save()

        # Mark appointment as completed (optional)
        appt.status = "COMPLETED"
        appt.save(update_fields=["status"])

        return Response(PrescriptionSerializer(pres).data, status=201)

    return Response(serializer.errors, status=400)


# --------------------------------------------------------------
# ADD PRESCRIPTION ITEM (MEDICINE)
# --------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDoctor])
def add_prescription_item(request, appt_id):
    doctor = StaffProfile.objects.get(user=request.user)

    try:
        appt = Appointment.objects.get(id=appt_id, doctor=doctor)
    except Appointment.DoesNotExist:
        return Response({"detail": "Not your appointment"}, status=404)

    try:
        pres = Prescription.objects.get(appointment=appt)
    except Prescription.DoesNotExist:
        return Response({"detail": "Prescription does not exist"}, status=400)

    serializer = PrescriptionItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(prescription=pres)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)



# --------------------------------------------------------------
# LAB ORDER
# --------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDoctor])
def create_lab_order(request, appt_id):
    doctor = StaffProfile.objects.get(user=request.user)

    try:
        appt = Appointment.objects.get(id=appt_id, doctor=doctor)
    except Appointment.DoesNotExist:
        return Response({"detail": "Appointment not found or not assigned to you"}, status=404)

    serializer = LabOrderSerializer(data={
        "appointment": appt.id,
        "doctor": doctor.id,
        "patient": appt.patient.id,
        "tests": request.data.get("tests", [])
    })

    if serializer.is_valid():
        order = serializer.save()

        total = sum(float(t.get("price", 0)) for t in (order.tests or []))

        if total > 0:
            BillingRecord.objects.create(
                bill_type="LAB",
                patient_name=appt.patient.full_name,
                amount=total,
                additional_info={
                    "lab_order_id": order.id,
                    "appointment_id": appt.id
                }
            )

        return Response(LabOrderSerializer(order).data, status=201)

    return Response(serializer.errors, status=400)


# --------------------------------------------------------------
# PHARMACY ORDER
# --------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDoctor])
def create_pharmacy_order(request, appt_id):
    doctor = StaffProfile.objects.get(user=request.user)

    try:
        appt = Appointment.objects.get(id=appt_id, doctor=doctor)
    except Appointment.DoesNotExist:
        return Response({"detail": "Appointment not found or not assigned to you"}, status=404)

    serializer = PharmacyOrderSerializer(data={
        "appointment": appt.id,
        "doctor": doctor.id,
        "patient": appt.patient.id,
        "items": request.data.get("items", [])
    })

    if serializer.is_valid():
        order = serializer.save()

        total = sum(
            float(i.get("price", 0)) * int(i.get("qty", 1))
            for i in (order.items or [])
        )

        if total > 0:
            BillingRecord.objects.create(
                bill_type="PHARMACY",
                patient_name=appt.patient.full_name,
                amount=total,
                additional_info={
                    "pharmacy_order_id": order.id,
                    "appointment_id": appt.id
                }
            )

        return Response(PharmacyOrderSerializer(order).data, status=201)

    return Response(serializer.errors, status=400)


# --------------------------------------------------------------
# MARK APPOINTMENT COMPLETE
# --------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDoctor])
def mark_appointment_completed(request, appt_id):
    doctor = StaffProfile.objects.get(user=request.user)

    try:
        appt = Appointment.objects.get(id=appt_id, doctor=doctor)
    except Appointment.DoesNotExist:
        return Response({"detail": "Appointment not found or not assigned to you"}, status=404)

    appt.status = "COMPLETED"
    appt.save(update_fields=["status"])

    return Response({"detail": "Appointment marked completed"})
