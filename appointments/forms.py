from django import forms
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        exclude = ['created_by', 'created_at', 'visit_start', 'visit_end', 'patient']
        widgets = {'appointment_date': forms.DateInput(attrs={'type': 'date'})}
