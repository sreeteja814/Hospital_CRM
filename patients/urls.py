from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('enquiries/', views.enquiry_list, name='enquiry_list'),
    path('enquiries/new/', views.enquiry_create, name='enquiry_create'),
    path('enquiries/<int:pk>/edit/', views.enquiry_update, name='enquiry_update'),
    path('enquiries/<int:pk>/convert/', views.enquiry_convert, name='enquiry_convert'),
    path('enquiries/<int:enquiry_id>/log-call/', views.calling_log_create, name='enquiry_log_call'),

    path('', views.patient_list, name='patient_list'),
    path('new/', views.patient_create, name='patient_create'),
    path('<int:pk>/', views.patient_detail, name='patient_detail'),
    path('<int:pk>/edit/', views.patient_update, name='patient_update'),
    path('<int:patient_id>/log-call/', views.calling_log_create, name='patient_log_call'),
    path('<int:patient_id>/followup/new/', views.followup_create, name='followup_create'),

    path('calls/', views.calling_log_list, name='calling_log_list'),
    path('followups/', views.followup_list, name='followup_list'),

    path('treatments/', views.treatment_list, name='treatment_list'),
    path('treatments/new/', views.treatment_create, name='treatment_create'),
    path('treatments/<int:pk>/edit/', views.treatment_update, name='treatment_update'),
]
