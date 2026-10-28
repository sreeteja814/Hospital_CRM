from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('schedule/', views.doctor_schedule, name='doctor_schedule'),
    path('patient/<int:patient_id>/new/', views.appointment_create, name='appointment_create_for_patient'),
    path('<int:pk>/status/', views.appointment_update_status, name='appointment_update_status'),
    path('available-slots/', views.available_slots, name='available_slots'),
]
