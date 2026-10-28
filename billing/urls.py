from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('patient/<int:patient_id>/new/', views.invoice_create, name='invoice_create_for_patient'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
]
