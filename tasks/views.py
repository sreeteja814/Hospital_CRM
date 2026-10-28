from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date', 'priority']
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'}), 'description': forms.Textarea(attrs={'rows': 2})}


@login_required
def task_list(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.assigned_by = request.user
            t.save()
            messages.success(request, 'Task created.')
            return redirect('tasks:task_list')
    else:
        form = TaskForm(initial={'assigned_to': request.user.id})
    return render(request, 'tasks/task_list.html', {'tasks': tasks, 'form': form})


@login_required
def task_mark_done(request, pk):
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    task.status = Task.Status.DONE
    task.save()
    return redirect('tasks:task_list')
