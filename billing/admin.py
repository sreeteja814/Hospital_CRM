from django.contrib import admin
from .models import Invoice, InvoiceItem, Payment


class ItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'patient', 'branch', 'invoice_date', 'status', 'payment_mode', 'total_amount', 'balance_due')
    list_filter = ('branch', 'status', 'payment_mode')
    search_fields = ('invoice_no', 'patient__name', 'patient__reg_id')
    readonly_fields = ('invoice_no',)
    inlines = [ItemInline, PaymentInline]
    date_hierarchy = 'invoice_date'
