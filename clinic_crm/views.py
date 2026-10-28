from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from patients.models import Enquiry, Patient
from appointments.models import Appointment
from tasks.models import Task


@login_required
def dashboard(request):
    today = date.today()
    week_ago = today - timedelta(days=7)

    stats = {
        'new_enquiries_today': Enquiry.objects.filter(created_at__date=today).count(),
        'total_patients': Patient.objects.count(),
        'appointments_today': Appointment.objects.filter(appointment_date=today).count(),
        'missed_consultations': Appointment.objects.filter(appointment_date__lt=today, status=Appointment.Status.SCHEDULED).count(),
        'pending_followups': Enquiry.objects.filter(next_calling_date__lte=today).exclude(status__in=[Enquiry.Status.CONVERTED, Enquiry.Status.LOST]).count(),
        'my_open_tasks': Task.objects.filter(assigned_to=request.user).exclude(status=Task.Status.DONE).count(),
    }

    lead_source_breakdown = (
        Enquiry.objects.filter(created_at__date__gte=week_ago)
        .values('lead_source__name').annotate(total=Count('id')).order_by('-total')[:8]
    )

    upcoming_appointments = Appointment.objects.filter(appointment_date__gte=today).select_related('patient', 'doctor', 'branch').order_by('appointment_date', 'slot_time')[:8]
    todays_tasks = Task.objects.filter(assigned_to=request.user).exclude(status=Task.Status.DONE)[:8]

    return render(request, 'dashboard.html', {
        'stats': stats, 'lead_source_breakdown': lead_source_breakdown,
        'upcoming_appointments': upcoming_appointments, 'todays_tasks': todays_tasks,
    })
