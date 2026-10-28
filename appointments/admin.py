from django.contrib import admin
from .models import DoctorSlot, Appointment


@admin.register(DoctorSlot)
class DoctorSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'branch', 'weekday', 'start_time', 'end_time', 'slot_length_minutes', 'is_active')
    list_filter = ('branch', 'weekday', 'is_active')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'branch', 'doctor', 'appt_type', 'appointment_date', 'slot_time', 'status', 'consult_fee', 'payment_due')
    list_filter = ('branch', 'status', 'appt_type', 'doctor')
    search_fields = ('patient__name', 'patient__reg_id', 'patient__mobile_number')
    date_hierarchy = 'appointment_date'
