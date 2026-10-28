from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from accounts.permissions import role_required
from accounts.models import User

from .models import Invoice
from .forms import InvoiceForm, InvoiceItemFormSet, PaymentForm
from patients.models import Patient


@role_required(*User.BILLING_ROLES)
def invoice_list(request):
    invoices = Invoice.objects.select_related('patient', 'branch')[:200]
    return render(request, 'billing/invoice_list.html', {'invoices': invoices})


@role_required(*User.BILLING_ROLES)
def invoice_create(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = None
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.patient = patient
            invoice.created_by = request.user
            invoice.save()
            formset = InvoiceItemFormSet(request.POST, instance=invoice)
            if formset.is_valid():
                formset.save()
                messages.success(request, f'Invoice {invoice.invoice_no} created.')
                return redirect('billing:invoice_detail', pk=invoice.pk)
        if formset is None:
            formset = InvoiceItemFormSet(request.POST)
    else:
        form = InvoiceForm(initial={'branch': patient.branch_id})
        formset = InvoiceItemFormSet()
    return render(request, 'billing/invoice_form.html', {'form': form, 'formset': formset, 'patient': patient})


@role_required(*User.BILLING_ROLES)
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        pform = PaymentForm(request.POST)
        if pform.is_valid():
            payment = pform.save(commit=False)
            payment.invoice = invoice
            payment.received_by = request.user
            payment.save()
            if invoice.balance_due <= 0:
                invoice.status = Invoice.Status.PAID
            else:
                invoice.status = Invoice.Status.PARTIAL
            invoice.save()
            messages.success(request, 'Payment recorded.')
            return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        pform = PaymentForm()
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice, 'pform': pform})


@role_required(*User.BILLING_ROLES)
def invoice_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    html = render_to_string('billing/invoice_pdf.html', {'invoice': invoice})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{invoice.invoice_no}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response
