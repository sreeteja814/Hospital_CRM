from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from accounts.permissions import role_required
from accounts.models import User
from notifications.services import send_whatsapp_message

from .models import Enquiry, Patient, CallingLog, FollowupVisit, Treatment, PatientReferral, PatientComplaint
from .forms import (
    EnquiryForm, PatientForm, CallingLogForm, FollowupVisitForm, PatientFamilyForm,
    TreatmentForm, PatientReferralForm, PatientComplaintForm
)


@role_required(*User.PATIENT_ROLES)
def enquiry_list(request):
    q = request.GET.get('q', '')
    enquiries = Enquiry.objects.select_related('branch', 'assign_doctor', 'lead_source')
    if q:
        enquiries = enquiries.filter(patient_name__icontains=q) | enquiries.filter(contact_number__icontains=q)
    return render(request, 'patients/enquiry_list.html', {'enquiries': enquiries[:200], 'q': q})


@role_required(*User.PATIENT_ROLES)
def enquiry_create(request):
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.created_by = request.user
            enquiry.save()
            form.save_m2m()
            messages.success(request, 'Enquiry saved.')
            return redirect('patients:enquiry_list')
    else:
        form = EnquiryForm()
    return render(request, 'patients/enquiry_form.html', {'form': form, 'title': 'Enquiry Form'})


@role_required(*User.PATIENT_ROLES)
def enquiry_update(request, pk):
    enquiry = get_object_or_404(Enquiry, pk=pk)
    if request.method == 'POST':
        form = EnquiryForm(request.POST, instance=enquiry)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enquiry updated.')
            return redirect('patients:enquiry_list')
    else:
        form = EnquiryForm(instance=enquiry)
    return render(request, 'patients/enquiry_form.html', {'form': form, 'title': f'Edit Enquiry - {enquiry.patient_name}'})


@role_required(*User.PATIENT_ROLES)
def enquiry_convert(request, pk):
    enquiry = get_object_or_404(Enquiry, pk=pk)
    if enquiry.converted_patient:
        messages.info(request, 'This enquiry is already converted.')
        return redirect('patients:patient_detail', pk=enquiry.converted_patient.pk)

    patient = Patient.objects.create(
        name=enquiry.patient_name,
        age=enquiry.age,
        gender=enquiry.gender,
        area=enquiry.area,
        city=enquiry.city_name,
        mobile_number=enquiry.contact_number,
        whatsapp_number=enquiry.whatsapp_number,
        alternative_number1=enquiry.alternative_number1,
        alternative_number2=enquiry.alternative_number2,
        speaking_language=enquiry.speaking_language,
        priority=enquiry.patient_priority,
        branch=enquiry.branch,
        treatments=enquiry.treatments,
        lead_source=enquiry.lead_source,
        assigned_doctor=enquiry.assign_doctor,
        consult_fee=enquiry.consultation_fee or 0,
        registration_date=enquiry.appointment_date,
        created_by=request.user,
    )
    enquiry.converted_patient = patient
    enquiry.status = Enquiry.Status.CONVERTED
    enquiry.save()
    messages.success(request, f'Converted to patient {patient.reg_id}.')
    return redirect('patients:patient_detail', pk=patient.pk)


@role_required(*User.PATIENT_ROLES)
def patient_list(request):
    q = request.GET.get('q', '')
    patients = Patient.objects.select_related('branch', 'assigned_doctor')
    if q:
        patients = patients.filter(name__icontains=q) | patients.filter(mobile_number__icontains=q) | patients.filter(reg_id__icontains=q)
    return render(request, 'patients/patient_list.html', {'patients': patients[:200], 'q': q})


@role_required(*User.PATIENT_ROLES)
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.save()
            form.save_m2m()
            messages.success(request, f'Patient {patient.reg_id} created.')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = PatientForm()
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'New Patient'})


@role_required(*User.PATIENT_ROLES)
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient details updated.')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/patient_form.html', {'form': form, 'title': f'Edit Patient - {patient.name}'})


@role_required(*User.PATIENT_ROLES)
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    family_form = PatientFamilyForm()
    referral_form = PatientReferralForm()
    complaint_form = PatientComplaintForm()

    if request.method == 'POST':
        if 'add_family' in request.POST:
            family_form = PatientFamilyForm(request.POST)
            if family_form.is_valid():
                member = family_form.save(commit=False)
                member.patient = patient
                member.save()
                messages.success(request, 'Family member added.')
                return redirect('patients:patient_detail', pk=patient.pk)
        elif 'add_referral' in request.POST:
            referral_form = PatientReferralForm(request.POST)
            if referral_form.is_valid():
                ref = referral_form.save(commit=False)
                ref.patient = patient
                ref.created_by = request.user
                ref.save()
                messages.success(request, 'Referral logged.')
                return redirect('patients:patient_detail', pk=patient.pk)
        elif 'add_complaint' in request.POST:
            complaint_form = PatientComplaintForm(request.POST)
            if complaint_form.is_valid():
                c = complaint_form.save(commit=False)
                c.patient = patient
                c.created_by = request.user
                c.save()
                messages.success(request, 'Complaint logged.')
                return redirect('patients:patient_detail', pk=patient.pk)

    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'family_form': family_form,
        'referral_form': referral_form,
        'complaint_form': complaint_form,
        'appointments': patient.appointments.all()[:10],
        'consultations': patient.consultations.all()[:10],
        'invoices': patient.invoices.all()[:10],
        'calling_logs': patient.calling_logs.all()[:10],
        'referrals': patient.referrals.all()[:10],
        'complaints': patient.complaints.all()[:10],
    })


@role_required(*User.PATIENT_ROLES)
def calling_log_list(request):
    logs = CallingLog.objects.select_related('called_by', 'patient', 'enquiry')[:200]
    return render(request, 'patients/calling_log_list.html', {'logs': logs})


@role_required(*User.PATIENT_ROLES)
def calling_log_create(request, enquiry_id=None, patient_id=None):
    enquiry = get_object_or_404(Enquiry, pk=enquiry_id) if enquiry_id else None
    patient = get_object_or_404(Patient, pk=patient_id) if patient_id else None
    if request.method == 'POST':
        form = CallingLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.called_by = request.user
            log.enquiry = enquiry
            log.patient = patient
            log.save()
            if log.message_send_to_customer:
                to_number = (patient.whatsapp_number or patient.mobile_number) if patient else (enquiry.whatsapp_number or enquiry.contact_number)
                name = patient.name if patient else enquiry.patient_name
                text = (
                    f"Hi {name}, this is {log.called_by.branch or 'our clinic'}. "
                    f"Regarding your recent call: {log.comments or 'we will follow up with you shortly.'}"
                )
                send_whatsapp_message(to_number, text, patient=patient, enquiry=enquiry)
            messages.success(request, 'Call logged.')
            if enquiry:
                return redirect('patients:enquiry_list')
            if patient:
                return redirect('patients:patient_detail', pk=patient.pk)
            return redirect('patients:calling_log_list')
    else:
        form = CallingLogForm()
    return render(request, 'patients/calling_log_form.html', {'form': form, 'enquiry': enquiry, 'patient': patient})


@role_required(*User.PATIENT_ROLES)
def followup_list(request):
    followups = FollowupVisit.objects.select_related('patient', 'recorded_by')[:200]
    return render(request, 'patients/followup_list.html', {'followups': followups})


@role_required(*User.PATIENT_ROLES)
def followup_create(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = FollowupVisitForm(request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            f.patient = patient
            f.recorded_by = request.user
            f.save()
            messages.success(request, 'Follow-up visit recorded.')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = FollowupVisitForm()
    return render(request, 'patients/followup_form.html', {'form': form, 'patient': patient})


@role_required(User.Role.ADMIN)
def treatment_list(request):
    treatments = Treatment.objects.all()
    return render(request, 'patients/treatment_list.html', {'treatments': treatments})


@role_required(User.Role.ADMIN)
def treatment_create(request):
    if request.method == 'POST':
        form = TreatmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Treatment added.')
            return redirect('patients:treatment_list')
    else:
        form = TreatmentForm()
    return render(request, 'patients/treatment_form.html', {'form': form, 'title': 'Add Treatment'})


@role_required(User.Role.ADMIN)
def treatment_update(request, pk):
    treatment = get_object_or_404(Treatment, pk=pk)
    if request.method == 'POST':
        form = TreatmentForm(request.POST, instance=treatment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Treatment updated.')
            return redirect('patients:treatment_list')
    else:
        form = TreatmentForm(instance=treatment)
    return render(request, 'patients/treatment_form.html', {'form': form, 'title': f'Edit Treatment - {treatment.name}'})
