from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('patient/<int:patient_id>/new/', views.consultation_create, name='consultation_create'),
    path('patient/<int:patient_id>/case-sheet/', views.case_sheet_list, name='case_sheet_list'),
    path('<int:pk>/prescription-pdf/', views.prescription_pdf, name='prescription_pdf'),
]
