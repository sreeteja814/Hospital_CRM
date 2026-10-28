from django import forms
from .models import (
    Enquiry, Patient, PatientFamilyMember, PatientReferral, PatientComplaint,
    CallingLog, FollowupVisit, Treatment
)


class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        exclude = ['status', 'converted_patient', 'created_by', 'created_at', 'updated_at']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'next_calling_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 2}),
            'treatments': forms.TextInput(attrs={'placeholder': 'e.g. Vitiligo, Joint Pain'}),
        }


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ['reg_id', 'created_by', 'created_at']
        widgets = {
            'treatments': forms.TextInput(attrs={'placeholder': 'e.g. Vitiligo, Joint Pain'}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'registration_date': forms.DateInput(attrs={'type': 'date'}),
            'registration_end_date': forms.DateInput(attrs={'type': 'date'}),
            'renewal_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PatientFamilyForm(forms.ModelForm):
    class Meta:
        model = PatientFamilyMember
        exclude = ['patient']


class PatientReferralForm(forms.ModelForm):
    class Meta:
        model = PatientReferral
        exclude = ['patient', 'created_by', 'created_at']


class PatientComplaintForm(forms.ModelForm):
    class Meta:
        model = PatientComplaint
        exclude = ['patient', 'created_by', 'created_at']
        widgets = {'complaint': forms.Textarea(attrs={'rows': 3})}


class CallingLogForm(forms.ModelForm):
    class Meta:
        model = CallingLog
        exclude = ['called_by', 'created_at']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'next_calling_date': forms.DateInput(attrs={'type': 'date'}),
            'medicine_start_date': forms.DateInput(attrs={'type': 'date'}),
            'medicine_end_date': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 2}),
        }


class FollowupVisitForm(forms.ModelForm):
    class Meta:
        model = FollowupVisit
        exclude = ['patient', 'recorded_by', 'created_at']
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class TreatmentForm(forms.ModelForm):
    class Meta:
        model = Treatment
        fields = ['name', 'default_consultation_fee', 'is_active']
