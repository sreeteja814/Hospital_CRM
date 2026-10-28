from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('<int:pk>/done/', views.task_mark_done, name='task_mark_done'),
]
