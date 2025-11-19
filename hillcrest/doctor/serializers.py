from rest_framework import serializers
from .models import Prescription, PrescriptionItem, LabOrder, PharmacyOrder


# -------------------------------------------------------
# PRESCRIPTION ITEM
# -------------------------------------------------------
class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = ("id", "medicine_name", "dosage", "duration", "instructions")


# -------------------------------------------------------
# PRESCRIPTION
# -------------------------------------------------------
class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, required=False)

    class Meta:
        model = Prescription
        fields = (
            "id",
            "appointment",
            "doctor",
            "patient",
            "notes",
            "diagnosis",
            "items",
            "created_at"
        )
        read_only_fields = ("doctor", "created_at")

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        prescription = Prescription.objects.create(**validated_data)

        for item_data in items_data:
            PrescriptionItem.objects.create(prescription=prescription, **item_data)

        return prescription


# -------------------------------------------------------
# LAB ORDER
# -------------------------------------------------------
class LabOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabOrder
        fields = "__all__"
        read_only_fields = ("doctor", "created_at")


# -------------------------------------------------------
# PHARMACY ORDER
# -------------------------------------------------------
class PharmacyOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyOrder
        fields = "__all__"
        read_only_fields = ("doctor", "created_at")
