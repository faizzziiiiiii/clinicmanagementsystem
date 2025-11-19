# doctor/admin.py
from django.contrib import admin
from .models import Prescription, PrescriptionItem, LabOrder, PharmacyOrder

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id","appointment","doctor","patient","created_at")
    search_fields = ("patient__full_name","doctor__user__username")

@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ("id","prescription","medicine_name","dosage")

@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ("id","appointment","doctor","patient","is_processed","created_at")
    search_fields = ("patient__full_name","doctor__user__username")

@admin.register(PharmacyOrder)
class PharmacyOrderAdmin(admin.ModelAdmin):
    list_display = ("id","appointment","doctor","patient","is_dispensed","created_at")
    search_fields = ("patient__full_name","doctor__user__username")
