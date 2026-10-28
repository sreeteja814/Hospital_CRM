from django.conf import settings
from django.db import models
from patients.models import Patient
from branches.models import Branch


class Invoice(models.Model):
    class PaymentMode(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CARD = 'CARD', 'Card'
        UPI = 'UPI', 'UPI'
        NET_BANKING = 'NET_BANKING', 'Net Banking'
        INSURANCE = 'INSURANCE', 'Insurance'
        CHEQUE = 'CHEQUE', 'Cheque'

    class Status(models.TextChoices):
        PAID = 'PAID', 'Paid'
        PARTIAL = 'PARTIAL', 'Partially Paid'
        DUE = 'DUE', 'Due'
        CANCELLED = 'CANCELLED', 'Cancelled'

    invoice_no = models.CharField(max_length=30, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='invoices')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='invoices')
    invoice_date = models.DateField()
    payment_mode = models.CharField(max_length=15, choices=PaymentMode.choices, default=PaymentMode.CASH)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DUE)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-invoice_date', '-id']

    def save(self, *args, **kwargs):
        if not self.invoice_no:
            last_id = (Invoice.objects.order_by('id').last().id if Invoice.objects.exists() else 0) + 1
            self.invoice_no = f"INV-{last_id:06d}"
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return sum(item.amount for item in self.items.all()) - self.discount

    @property
    def amount_paid(self):
        return sum(p.amount for p in self.payments.all())

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

    def __str__(self):
        return f"{self.invoice_no} - {self.patient.name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def amount(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.description} x{self.quantity}"


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateField()
    mode = models.CharField(max_length=15, choices=Invoice.PaymentMode.choices, default=Invoice.PaymentMode.CASH)
    reference_no = models.CharField(max_length=80, blank=True, help_text="Receipt no. / transaction ref.")
    manual_receipt_no = models.CharField(max_length=80, blank=True)
    cheque_no = models.CharField(max_length=50, blank=True)
    cheque_status = models.CharField(max_length=30, blank=True, help_text="e.g. Cleared, Bounced, Stopped")
    cheque_date = models.DateField(null=True, blank=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Payment {self.amount} for {self.invoice.invoice_no}"
