from django.conf import settings
from django.db import models
from branches.models import Branch
from patients.models import Patient, Treatment


class DoctorSlot(models.Model):
    WEEKDAYS = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
        (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='slots')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='doctor_slots')
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_length_minutes = models.PositiveIntegerField(default=15, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['weekday', 'start_time']

    def __str__(self):
        return f"{self.doctor} @ {self.branch} - {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    class ApptType(models.TextChoices):
        ENQUIRY = 'ENQUIRY', 'Enquiry'
        FOLLOW_UP = 'FOLLOW_UP', 'Follow Up Appt'
        MEDICINE_PICKUP = 'MEDICINE_PICKUP', 'Medicine Pick-Up Appt'
        PROCEDURE = 'PROCEDURE', 'Procedure'

    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        VISITED = 'VISITED', 'Visited'
        NO_SHOW = 'NO_SHOW', 'No Show'
        CANCELLED = 'CANCELLED', 'Cancelled'

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='appointments')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    treatment = models.ForeignKey(Treatment, on_delete=models.SET_NULL, null=True, blank=True)
    appt_type = models.CharField(max_length=20, choices=ApptType.choices, default=ApptType.ENQUIRY)
    appointment_date = models.DateField()
    slot_time = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    visit_start = models.DateTimeField(null=True, blank=True)
    visit_end = models.DateTimeField(null=True, blank=True)
    consult_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    payment_due = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['appointment_date', 'slot_time']

    def __str__(self):
        return f"{self.patient.name} - {self.appointment_date} ({self.get_status_display()})"
