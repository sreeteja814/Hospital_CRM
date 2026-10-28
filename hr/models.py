from django.conf import settings
from django.db import models
from branches.models import Branch


class Employee(models.Model):
    class EmploymentStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        ON_LEAVE = 'ON_LEAVE', 'On Leave'
        RESIGNED = 'RESIGNED', 'Resigned'
        TERMINATED = 'TERMINATED', 'Terminated'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile')
    employee_code = models.CharField(max_length=30, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    date_of_joining = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=EmploymentStatus.choices, default=EmploymentStatus.ACTIVE)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.employee_code} - {self.user.get_full_name() or self.user.username}"


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        HALF_DAY = 'HALF_DAY', 'Half Day'
        LEAVE = 'LEAVE', 'On Leave'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"


class Incentive(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='incentives')
    month = models.DateField(help_text="Use the 1st of the month this incentive applies to")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-month']

    def __str__(self):
        return f"{self.employee} - {self.month:%b %Y} - {self.amount}"
