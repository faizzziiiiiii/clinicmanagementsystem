from django.urls import path
from . import views

urlpatterns = [
    path("my-appointments/", views.my_appointments),

    # Appointment Detail
    path("appointments/<int:appt_id>/", views.appointment_detail),

    # Create prescription (doctor’s notes)
    path("appointments/<int:appt_id>/prescription/", views.create_prescription),

    # Add prescription item (medicine)
    path(
        "appointments/<int:appt_id>/prescription/add-item/",
        views.add_prescription_item
    ),

    # Lab order
    path("appointments/<int:appt_id>/lab-order/", views.create_lab_order),

    # Pharmacy order
    path("appointments/<int:appt_id>/pharmacy-order/", views.create_pharmacy_order),

    # Complete appointment
    path("appointments/<int:appt_id>/complete/", views.mark_appointment_completed),
]
