from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', views.dashboard, name='dashboard'),
    path('patients/', include('patients.urls')),
    path('appointments/', include('appointments.urls')),
    path('consultations/', include('consultations.urls')),
    path('billing/', include('billing.urls')),
    path('hr/', include('hr.urls')),
    path('tasks/', include('tasks.urls')),
    path('notifications/', include('notifications.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
