from django.contrib import admin
from .models import Consultation, ConsultationDocument, Prescription, ConsultationMessage


class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 1


class DocInline(admin.TabularInline):
    model = ConsultationDocument
    extra = 0


class MessageInline(admin.TabularInline):
    model = ConsultationMessage
    extra = 0
    fields = ('from_designation', 'message', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'consulted_date', 'doctor', 'treatment', 'patient_status', 'followup_date')
    list_filter = ('doctor', 'treatment', 'patient_status')
    search_fields = ('patient__name', 'patient__reg_id')
    date_hierarchy = 'consulted_date'
    inlines = [PrescriptionInline, DocInline, MessageInline]
    fieldsets = (
        ('Visit', {'fields': ('patient', 'appointment', 'doctor', 'treatment', 'consulted_date')}),
        ('Preliminary Data', {'fields': ('presenting_complaints', 'personal_history')}),
        ('Vitals / General Examination', {'fields': ('bp', 'pulse', 'weight_kg', 'height_cm', 'temperature', 'bmi', 'systemic_examination')}),
        ('Homeopathic Case-Taking', {'fields': (
            'particular', 'mental_general', 'physical_general', 'miasmatic_diagnosis',
            'repertorial_result', 'analysis_evaluation',
        )}),
        ('Plan', {'fields': (
            'management', 'diet', 'exercises', 'nutrition', 'present_medication',
            'level_of_assurance', 'criteria_future_plan_rx', 'dos_and_donts',
        )}),
        ('Clinical Observation', {'fields': (
            'clinical_observation', 'progress', 'suggested_duration', 'package_duration',
            'package_end_date', 'medicine_days', 'followup_date', 'patient_status',
        )}),
    )
