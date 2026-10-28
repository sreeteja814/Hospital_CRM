from datetime import date, timedelta
from django.shortcuts import render
from django.db.models import Count, Sum, Q, Max

from accounts.permissions import role_required
from accounts.models import User
from patients.models import Enquiry, Patient, CallingLog
from appointments.models import Appointment
from hr.models import Incentive


@role_required(*User.REPORTS_ROLES)
def reports_dashboard(request):
    today = date.today()
    appointments_by_status = Appointment.objects.values('status').annotate(total=Count('id'))
    leads_by_source = Enquiry.objects.values('lead_source__name').annotate(total=Count('id')).order_by('-total')[:10]
    return render(request, 'reports/dashboard.html', {
        'appointments_by_status': appointments_by_status,
        'leads_by_source': leads_by_source,
    })


@role_required(*User.REPORTS_ROLES)
def appointments_report(request):
    appointments = Appointment.objects.select_related('patient', 'doctor', 'branch').order_by('-appointment_date')[:300]
    return render(request, 'reports/appointments_report.html', {'appointments': appointments})


@role_required(*User.REPORTS_ROLES)
def appointments_slot_report(request):
    day = request.GET.get('date', date.today().isoformat())
    slots = (
        Appointment.objects.filter(appointment_date=day)
        .values('slot_time', 'doctor__first_name', 'doctor__last_name')
        .annotate(total=Count('id'))
        .order_by('slot_time')
    )
    return render(request, 'reports/appointments_slot_report.html', {'slots': slots, 'day': day})


@role_required(*User.REPORTS_ROLES)
def doctor_appointments_report(request):
    """Appointments grouped by doctor — how many each doctor has, by status."""
    doctors = (
        User.objects.filter(role__in=['DOCTOR', 'ENQ_DOCTOR'])
        .annotate(
            scheduled=Count('appointments', filter=Q(appointments__status='SCHEDULED'), distinct=True),
            visited=Count('appointments', filter=Q(appointments__status='VISITED'), distinct=True),
            no_show=Count('appointments', filter=Q(appointments__status='NO_SHOW'), distinct=True),
            total=Count('appointments', distinct=True),
        )
    )
    return render(request, 'reports/doctor_appointments_report.html', {'doctors': doctors})


@role_required(*User.REPORTS_ROLES)
def doctor_report(request):
    doctors = (
        User.objects.filter(role__in=['DOCTOR', 'ENQ_DOCTOR'])
        .annotate(
            total_patients=Count('patients', distinct=True),
            total_appointments=Count('appointments', distinct=True),
            total_consultations=Count('consultations_done', distinct=True),
        )
    )
    return render(request, 'reports/doctor_report.html', {'doctors': doctors})


@role_required(*User.REPORTS_ROLES)
def enquiry_doctor_performance_report(request):
    doctors = (
        User.objects.filter(role='ENQ_DOCTOR')
        .annotate(
            total_enquiries=Count('assigned_enquiries', distinct=True),
            converted=Count('assigned_enquiries', filter=Q(assigned_enquiries__status='CONVERTED'), distinct=True),
            lost=Count('assigned_enquiries', filter=Q(assigned_enquiries__status='LOST'), distinct=True),
        )
    )
    return render(request, 'reports/enquiry_doctor_performance.html', {'doctors': doctors})


@role_required(*User.REPORTS_ROLES)
def enquiry_doctor_inactive_patients_report(request):
    """Patients whose assigned enquiry doctor hasn't had a followup/call in 30+ days."""
    cutoff = date.today() - timedelta(days=30)
    patients = (
        Patient.objects.select_related('assigned_doctor', 'branch')
        .annotate(last_call=Max('calling_logs__created_at'))
        .filter(Q(last_call__lt=cutoff) | Q(last_call__isnull=True))
    )
    return render(request, 'reports/enquiry_doctor_inactive_patients.html', {'patients': patients, 'cutoff': cutoff})


@role_required(*User.REPORTS_ROLES)
def enquiry_doctor_ownership_report(request):
    """How many patients each staff member 'owns' (enquiry ownership / unit ownership)."""
    doctors = (
        User.objects.filter(role__in=['DOCTOR', 'ENQ_DOCTOR', 'FDO'])
        .annotate(
            enquiry_owned=Count('patients_owned_enquiry', distinct=True),
            unit_owned=Count('patients_owned_unit', distinct=True),
        )
        .filter(Q(enquiry_owned__gt=0) | Q(unit_owned__gt=0))
    )
    return render(request, 'reports/enquiry_doctor_ownership_report.html', {'doctors': doctors})


@role_required(*User.REPORTS_ROLES)
def unit_doctor_ownership_report(request):
    doctors = (
        User.objects.filter(role__in=['DOCTOR', 'ENQ_DOCTOR'])
        .annotate(unit_owned=Count('patients_as_senior_doctor', distinct=True) + Count('patients_as_renewal_doctor', distinct=True))
    )
    return render(request, 'reports/unit_doctor_ownership_report.html', {'doctors': doctors})


@role_required(*User.REPORTS_ROLES)
def medicine_calling_report(request):
    """Calling logs where medicine tracking is overdue or due soon."""
    logs = (
        CallingLog.objects.select_related('patient', 'called_by')
        .filter(medicine_end_date__isnull=False)
        .order_by('medicine_end_date')[:300]
    )
    return render(request, 'reports/medicine_calling_report.html', {'logs': logs})


@role_required(*User.HR_ROLES)
def employee_incentive_report(request):
    incentives = Incentive.objects.select_related('employee__user').order_by('-month')[:200]
    return render(request, 'reports/employee_incentive_report.html', {'incentives': incentives})


@role_required(*User.REPORTS_ROLES)
def followup_calling_report(request):
    """Under the 'Master' menu — filterable follow-up calling log report."""
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    logs = CallingLog.objects.select_related('patient', 'enquiry', 'called_by').order_by('-created_at')
    if from_date:
        logs = logs.filter(created_at__date__gte=from_date)
    if to_date:
        logs = logs.filter(created_at__date__lte=to_date)
    return render(request, 'reports/followup_calling_report.html', {
        'logs': logs[:300], 'from_date': from_date, 'to_date': to_date,
    })
