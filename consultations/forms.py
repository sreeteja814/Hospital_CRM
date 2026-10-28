from django import forms
from django.forms import inlineformset_factory
from .models import Consultation, Prescription


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        exclude = ['patient', 'created_at']
        widgets = {
            'consulted_date': forms.DateInput(attrs={'type': 'date'}),
            'package_end_date': forms.DateInput(attrs={'type': 'date'}),
            'followup_date': forms.DateInput(attrs={'type': 'date'}),
            'presenting_complaints': forms.Textarea(attrs={'rows': 3}),
            'personal_history': forms.Textarea(attrs={'rows': 2}),
            'systemic_examination': forms.Textarea(attrs={'rows': 2}),
            'particular': forms.Textarea(attrs={'rows': 2}),
            'mental_general': forms.Textarea(attrs={'rows': 2}),
            'physical_general': forms.Textarea(attrs={'rows': 2}),
            'repertorial_result': forms.Textarea(attrs={'rows': 2}),
            'analysis_evaluation': forms.Textarea(attrs={'rows': 2}),
            'management': forms.Textarea(attrs={'rows': 2}),
            'diet': forms.Textarea(attrs={'rows': 2}),
            'exercises': forms.Textarea(attrs={'rows': 2}),
            'present_medication': forms.Textarea(attrs={'rows': 2}),
            'criteria_future_plan_rx': forms.Textarea(attrs={'rows': 2}),
            'dos_and_donts': forms.Textarea(attrs={'rows': 2}),
            'clinical_observation': forms.Textarea(attrs={'rows': 4}),
        }


PrescriptionFormSet = inlineformset_factory(
    Consultation, Prescription,
    fields=['medicine_name', 'dosage', 'duration_days', 'notes'],
    extra=3, can_delete=True
)
