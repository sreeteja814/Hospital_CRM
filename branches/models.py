from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="Short code, e.g. BR1-KOMPALLY")
    city = models.CharField(max_length=80, blank=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    opening_time = models.TimeField(null=True, blank=True, help_text="Daily opening time, e.g. 10:30 AM")
    closing_time = models.TimeField(null=True, blank=True, help_text="Daily closing time, e.g. 8:00 PM")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    @property
    def hours_display(self):
        if self.opening_time and self.closing_time:
            return f"{self.opening_time.strftime('%I:%M %p').lstrip('0')} - {self.closing_time.strftime('%I:%M %p').lstrip('0')}, all days"
        return ""

    def __str__(self):
        return f"{self.code} - {self.name}"
