from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem, Payment


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        exclude = ['invoice_no', 'patient', 'created_by', 'created_at']
        widgets = {'invoice_date': forms.DateInput(attrs={'type': 'date'})}


InvoiceItemFormSet = inlineformset_factory(
    Invoice, InvoiceItem, fields=['description', 'quantity', 'unit_price'], extra=3, can_delete=True
)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        exclude = ['invoice', 'received_by']
        widgets = {'paid_on': forms.DateInput(attrs={'type': 'date'}), 'cheque_date': forms.DateInput(attrs={'type': 'date'})}
