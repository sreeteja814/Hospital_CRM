from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_log_list, name='log_list'),
]
