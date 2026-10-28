from django.shortcuts import render
from accounts.permissions import role_required
from accounts.models import User
from .models import NotificationLog


@role_required(*User.PATIENT_ROLES)
def notification_log_list(request):
    logs = NotificationLog.objects.select_related('patient', 'enquiry')[:200]
    return render(request, 'notifications/log_list.html', {'logs': logs})
