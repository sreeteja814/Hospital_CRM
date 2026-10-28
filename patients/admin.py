from django.contrib import admin
from .models import (
    LeadSource, Treatment, Patient, PatientFamilyMember, PatientReferral,
    PatientComplaint, Enquiry, CallingLog, FollowupVisit
)


@admin.register(LeadSource)
class LeadSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_consultation_fee', 'is_active')
    search_fields = ('name',)


class FamilyInline(admin.TabularInline):
    model = PatientFamilyMember
    extra = 0


class ReferralInline(admin.TabularInline):
    model = PatientReferral
    extra = 0
    fields = ('referred_name', 'referred_mobile', 'notes', 'created_at')
    readonly_fields = ('created_at',)


class ComplaintInline(admin.TabularInline):
    model = PatientComplaint
    extra = 0
    fields = ('complaint', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('reg_id', 'name', 'mobile_number', 'branch', 'assigned_doctor', 'priority',
                     'package_amount', 'paid_amount', 'balance_due', 'registration_end_date', 'cheque_stop_bounce', 'created_at')
    list_filter = ('branch', 'priority', 'gender', 'cheque_stop_bounce')
    search_fields = ('reg_id', 'name', 'mobile_number', 'whatsapp_number')
    inlines = [FamilyInline, ReferralInline, ComplaintInline]
    readonly_fields = ('reg_id',)
    fieldsets = (
        ('Identity', {'fields': ('reg_id', 'name', 'age', 'gender', 'marital_status', 'priority', 'treatments')}),
        ('Contact & Address', {'fields': (
            'mobile_number', 'whatsapp_number', 'alternative_number1', 'alternative_number2', 'email',
            'speaking_language', 'area', 'city', 'state', 'country', 'pincode', 'address',
        )}),
        ('Courier Address (for medicine delivery)', {'fields': (
            'courier_d_no', 'courier_area_address', 'courier_area_address2',
            'courier_city', 'courier_state', 'courier_country', 'courier_pincode',
        )}),
        ('Branch & Source', {'fields': ('branch', 'lead_source', 'source_of_information')}),
        ('Staff / Ownership', {'fields': (
            'assigned_doctor', 'senior_doctor', 'renewal_doctor', 'enquiry_ownership', 'unit_ownership',
            'cro_name', 'created_by',
        )}),
        ('Registration / Package', {'fields': (
            'registration_date', 'package_amount', 'package_duration_months', 'registration_end_date',
            'renewal_date', 'paid_amount', 'due_amount', 'refund_amount', 'consult_fee', 'cheque_stop_bounce',
        )}),
    )


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'contact_number', 'branch', 'status', 'assign_doctor',
                     'appointment_date', 'next_calling_date', 'created_at')
    list_filter = ('branch', 'status', 'enquiry_type', 'lead_source', 'patient_priority')
    search_fields = ('patient_name', 'contact_number', 'whatsapp_number')
    date_hierarchy = 'created_at'


@admin.register(CallingLog)
class CallingLogAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'called_by', 'call_status', 'calling_type', 'better_patient_percent',
                     'medicine_end_date', 'next_calling_date')
    list_filter = ('call_status', 'calling_type', 'criteria_grade')


@admin.register(FollowupVisit)
class FollowupVisitAdmin(admin.ModelAdmin):
    list_display = ('patient', 'visit_date', 'reason', 'recorded_by')
    list_filter = ('visit_date',)


@admin.register(PatientReferral)
class PatientReferralAdmin(admin.ModelAdmin):
    list_display = ('patient', 'referred_name', 'referred_mobile', 'created_at')
    search_fields = ('referred_mobile', 'referred_name', 'patient__name')


@admin.register(PatientComplaint)
class PatientComplaintAdmin(admin.ModelAdmin):
    list_display = ('patient', 'complaint', 'created_at')
    search_fields = ('patient__name',)
