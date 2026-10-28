from datetime import date
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from accounts.permissions import role_required
from accounts.models import User
from notifications.services import send_whatsapp_message

from .models import Appointment
from .forms import AppointmentForm
from .services import get_available_slots
from patients.models import Patient


@role_required(*User.PATIENT_ROLES)
def doctor_schedule(request):
    day = request.GET.get('date') or date.today().isoformat()
    appointments = Appointment.objects.select_related('patient', 'doctor', 'branch').filter(appointment_date=day)
    return render(request, 'appointments/doctor_schedule.html', {'appointments': appointments, 'day': day})


@role_required(*User.PATIENT_ROLES)
def appointment_create(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.patient = patient
            appt.created_by = request.user
            appt.save()
            send_whatsapp_message(
                patient.whatsapp_number or patient.mobile_number,
                f"Hi {patient.name}, your appointment is confirmed for {appt.appointment_date} "
                f"({appt.slot_time or 'time to be confirmed'}) at {appt.branch.name}.",
                patient=patient,
            )
            messages.success(request, 'Appointment booked.')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = AppointmentForm(initial={'branch': patient.branch_id, 'doctor': patient.assigned_doctor_id, 'consult_fee': patient.consult_fee})
    return render(request, 'appointments/appointment_form.html', {'form': form, 'patient': patient})


@role_required(*User.PATIENT_ROLES)
def appointment_update_status(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(Appointment.Status.choices):
        appt.status = new_status
        appt.save()
        messages.success(request, 'Status updated.')
    return redirect(request.META.get('HTTP_REFERER', 'appointments:doctor_schedule'))


@role_required(*User.PATIENT_ROLES)
def available_slots(request):
    doctor_id = request.GET.get('doctor')
    branch_id = request.GET.get('branch')
    day = request.GET.get('date')
    if not (doctor_id and branch_id and day):
        return JsonResponse({'slots': []})
    from django.contrib.auth import get_user_model
    from branches.models import Branch
    User_ = get_user_model()
    try:
        doctor = User_.objects.get(pk=doctor_id)
        branch = Branch.objects.get(pk=branch_id)
    except (User_.DoesNotExist, Branch.DoesNotExist):
        return JsonResponse({'slots': []})
    slots = get_available_slots(doctor, branch, day)
    return JsonResponse({'slots': slots})
