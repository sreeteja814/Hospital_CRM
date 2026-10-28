from django.contrib import admin
from .models import Employee, Attendance, Incentive


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_code', 'user', 'branch', 'status', 'date_of_joining', 'monthly_salary')
    list_filter = ('branch', 'status')
    search_fields = ('employee_code', 'user__username', 'user__first_name', 'user__last_name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'check_in', 'check_out')
    list_filter = ('status', 'date')
    date_hierarchy = 'date'


@admin.register(Incentive)
class IncentiveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'month', 'amount', 'reason')
    list_filter = ('month',)
