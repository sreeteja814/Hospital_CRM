from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from accounts.permissions import role_required
from accounts.models import User

from .models import Consultation
from .forms import ConsultationForm, PrescriptionFormSet
from patients.models import Patient


@role_required(*User.CLINICAL_ROLES)
def consultation_create(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        formset = None
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.patient = patient
            if not consultation.doctor_id:
                consultation.doctor = request.user
            consultation.save()
            formset = PrescriptionFormSet(request.POST, instance=consultation)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Case sheet saved.')
                return redirect('patients:patient_detail', pk=patient.pk)
        if formset is None:
            formset = PrescriptionFormSet(request.POST)
    else:
        form = ConsultationForm(initial={'doctor': request.user.id, 'treatment': None})
        formset = PrescriptionFormSet()
    return render(request, 'consultations/consultation_form.html', {'form': form, 'formset': formset, 'patient': patient})


@role_required(*User.PATIENT_ROLES)
def case_sheet_list(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    consultations = patient.consultations.select_related('doctor', 'treatment').prefetch_related('prescriptions')
    return render(request, 'consultations/case_sheet_list.html', {'patient': patient, 'consultations': consultations})


@role_required(*User.CLINICAL_ROLES)
def prescription_pdf(request, pk):
    consultation = get_object_or_404(Consultation, pk=pk)
    html = render_to_string('consultations/prescription_pdf.html', {'c': consultation})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="prescription-{consultation.patient.reg_id}-{consultation.consulted_date}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response
