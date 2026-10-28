from datetime import date
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django import forms

from accounts.permissions import role_required
from accounts.models import User
from .models import Employee, Attendance


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date', 'status', 'check_in', 'check_out']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in': forms.TimeInput(attrs={'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'type': 'time'}),
        }


@role_required(*User.HR_ROLES)
def employee_list(request):
    employees = Employee.objects.select_related('user', 'branch')
    return render(request, 'hr/employee_list.html', {'employees': employees})


@role_required(*User.HR_ROLES)
def employee_attendance(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            att = form.save(commit=False)
            att.employee = employee
            att.save()
            messages.success(request, 'Attendance marked.')
            return redirect('hr:employee_attendance', pk=employee.pk)
    else:
        form = AttendanceForm(initial={'date': date.today()})
    records = employee.attendance.all()[:30]
    return render(request, 'hr/employee_attendance.html', {'employee': employee, 'form': form, 'records': records})
