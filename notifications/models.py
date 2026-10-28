from django.db import models


class NotificationLog(models.Model):
    class Channel(models.TextChoices):
        WHATSAPP = 'WHATSAPP', 'WhatsApp'
        SMS = 'SMS', 'SMS'

    class Status(models.TextChoices):
        SENT = 'SENT', 'Sent'
        FAILED = 'FAILED', 'Failed'
        LOGGED_ONLY = 'LOGGED_ONLY', 'Logged only (no provider configured)'

    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.WHATSAPP)
    to_number = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.LOGGED_ONLY)
    provider_response = models.TextField(blank=True)
    patient = models.ForeignKey('patients.Patient', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    enquiry = models.ForeignKey('patients.Enquiry', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_channel_display()} to {self.to_number} - {self.get_status_display()}"
