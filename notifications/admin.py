from django.contrib import admin
from .models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('to_number', 'channel', 'status', 'patient', 'enquiry', 'created_at')
    list_filter = ('channel', 'status')
    search_fields = ('to_number', 'message')
    readonly_fields = [f.name for f in NotificationLog._meta.fields]
