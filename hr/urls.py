from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('<int:pk>/attendance/', views.employee_attendance, name='employee_attendance'),
]
