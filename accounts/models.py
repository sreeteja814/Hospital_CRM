from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        FDO = 'FDO', 'Front Desk Officer'
        ENQUIRY_DOCTOR = 'ENQ_DOCTOR', 'Enquiry Doctor'
        DOCTOR = 'DOCTOR', 'Doctor'
        HR = 'HR', 'HR'
        ACCOUNTS = 'ACCOUNTS', 'Accounts / Billing'
        PHARMACY = 'PHARMACY', 'Pharmacy'
        CALL_CENTER = 'CALL_CENTER', 'Call Center / Calling'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.FDO)
    branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='staff')
    phone = models.CharField(max_length=20, blank=True)
    designation = models.CharField(max_length=80, blank=True)

    FRONT_DESK_ROLES = [Role.ADMIN, Role.FDO, Role.CALL_CENTER]
    CLINICAL_ROLES = [Role.ADMIN, Role.DOCTOR, Role.ENQUIRY_DOCTOR]
    BILLING_ROLES = [Role.ADMIN, Role.ACCOUNTS, Role.FDO]
    HR_ROLES = [Role.ADMIN, Role.HR]
    PATIENT_ROLES = [Role.ADMIN, Role.FDO, Role.CALL_CENTER, Role.DOCTOR, Role.ENQUIRY_DOCTOR, Role.ACCOUNTS, Role.PHARMACY]
    REPORTS_ROLES = [Role.ADMIN, Role.FDO, Role.DOCTOR, Role.ENQUIRY_DOCTOR, Role.ACCOUNTS, Role.HR]

    @property
    def can_access_hr(self):
        return self.is_superuser or self.role in self.HR_ROLES

    @property
    def can_access_billing(self):
        return self.is_superuser or self.role in self.BILLING_ROLES

    @property
    def can_access_clinical(self):
        return self.is_superuser or self.role in self.CLINICAL_ROLES

    @property
    def can_access_patients(self):
        return self.is_superuser or self.role in self.PATIENT_ROLES

    @property
    def can_access_reports(self):
        return self.is_superuser or self.role in self.REPORTS_ROLES

    @property
    def is_admin_role(self):
        return self.is_superuser or self.role == self.Role.ADMIN

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
