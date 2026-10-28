from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('appointments/', views.appointments_report, name='appointments_report'),
    path('appointments/slots/', views.appointments_slot_report, name='appointments_slot_report'),
    path('doctors/', views.doctor_report, name='doctor_report'),
    path('doctor-appointments/', views.doctor_appointments_report, name='doctor_appointments_report'),
    path('enquiry-doctor-performance/', views.enquiry_doctor_performance_report, name='enquiry_doctor_performance'),
    path('enquiry-doctor-inactive-patients/', views.enquiry_doctor_inactive_patients_report, name='enquiry_doctor_inactive_patients'),
    path('enquiry-doctor-ownership/', views.enquiry_doctor_ownership_report, name='enquiry_doctor_ownership'),
    path('unit-doctor-ownership/', views.unit_doctor_ownership_report, name='unit_doctor_ownership'),
    path('medicine-calling/', views.medicine_calling_report, name='medicine_calling_report'),
    path('employee-incentives/', views.employee_incentive_report, name='employee_incentive_report'),
    path('followup-calling/', views.followup_calling_report, name='followup_calling_report'),
]
