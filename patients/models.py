from django.conf import settings
from django.db import models
from branches.models import Branch


class LeadSource(models.Model):
    """Marketing/lead source, e.g. Facebook, Google Maps, Just Dial, Employee Referral."""
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Treatment(models.Model):
    """A treatment/ailment category offered by the clinic — used for the doctor's
    consultation/appointment dropdowns. The patient/enquiry's own 'treatments' field
    is free text (see Patient/Enquiry below), not linked to this list."""
    name = models.CharField(max_length=120, unique=True)
    default_consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Patient(models.Model):
    """A confirmed/registered patient record (created once an Enquiry converts)."""

    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    class Priority(models.TextChoices):
        HIGH = 'HIGH', 'High'
        MEDIUM = 'MEDIUM', 'Medium'
        LOW = 'LOW', 'Low'

    class MaritalStatus(models.TextChoices):
        SINGLE = 'SINGLE', 'Single'
        MARRIED = 'MARRIED', 'Married'
        OTHER = 'OTHER', 'Other'

    # --- Identity ---
    reg_id = models.CharField(max_length=30, unique=True, editable=False)
    name = models.CharField(max_length=150)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    marital_status = models.CharField(max_length=10, choices=MaritalStatus.choices, blank=True)

    # --- Contact & address ---
    area = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default='India')
    pincode = models.CharField(max_length=12, blank=True)
    address = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    mobile_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    alternative_number1 = models.CharField(max_length=20, blank=True)
    alternative_number2 = models.CharField(max_length=20, blank=True)
    speaking_language = models.CharField(max_length=60, blank=True)

    # --- Courier address (for mailing medicines) ---
    courier_d_no = models.CharField(max_length=50, blank=True, verbose_name="Courier D.No")
    courier_area_address = models.CharField(max_length=255, blank=True)
    courier_area_address2 = models.CharField(max_length=255, blank=True)
    courier_city = models.CharField(max_length=100, blank=True)
    courier_state = models.CharField(max_length=100, blank=True)
    courier_country = models.CharField(max_length=100, blank=True, default='India')
    courier_pincode = models.CharField(max_length=12, blank=True)

    priority = models.CharField(max_length=10, choices=Priority.choices, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='patients')
    treatments = models.CharField(max_length=255, blank=True, default='', help_text="e.g. Vitiligo, Joint Pain")
    lead_source = models.ForeignKey(LeadSource, on_delete=models.SET_NULL, null=True, blank=True)
    source_of_information = models.CharField(max_length=100, blank=True, help_text="e.g. Inbound, Outbound, Walk-in")

    # --- Staff linked to this patient (mirrors the reference system's ownership roles) ---
    assigned_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='patients', verbose_name='Unit Doctor'
    )
    senior_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients_as_senior_doctor'
    )
    renewal_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients_as_renewal_doctor'
    )
    enquiry_ownership = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients_owned_enquiry'
    )
    unit_ownership = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients_owned_unit'
    )
    cro_name = models.CharField(max_length=150, blank=True, help_text="Call center rep / CRO handling this patient")

    # --- Registration / package (subscription-style billing) ---
    registration_date = models.DateField(null=True, blank=True)
    package_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    package_duration_months = models.PositiveIntegerField(null=True, blank=True)
    registration_end_date = models.DateField(null=True, blank=True, help_text="When this package/registration expires")
    renewal_date = models.DateField(null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    consult_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    cheque_stop_bounce = models.BooleanField(default=False, help_text="Flag if a cheque from this patient stopped or bounced")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='patients_created', verbose_name='Patient Reg By'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.reg_id:
            branch_code = (self.branch.code[:6] if self.branch_id else 'REG').upper()
            last = Patient.objects.filter(branch=self.branch).count() + 1
            self.reg_id = f"{branch_code}{last:04d}"
        super().save(*args, **kwargs)

    @property
    def balance_due(self):
        if self.package_amount is not None:
            return self.package_amount - self.paid_amount
        return self.due_amount

    def __str__(self):
        return f"{self.reg_id} - {self.name}"


class PatientFamilyMember(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='family_members')
    name = models.CharField(max_length=150)
    relation = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=20, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.name} ({self.relation} of {self.patient.name})"


class PatientReferral(models.Model):
    """A patient referring a new prospective patient — tracked for referral incentives."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='referrals')
    referred_name = models.CharField(max_length=150, blank=True)
    referred_mobile = models.CharField(max_length=20)
    notes = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.name} referred {self.referred_mobile}"


class PatientComplaint(models.Model):
    """A logged complaint from/about a patient, separate from clinical notes."""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='complaints')
    complaint = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Complaint for {self.patient.name} on {self.created_at:%d-%m-%Y}"


class Enquiry(models.Model):
    """A lead captured before becoming a Patient."""

    class EnquiryType(models.TextChoices):
        WALK_IN = 'WALK_IN', 'Walk In'
        PHONE = 'PHONE', 'Phone'
        VIDEO = 'VIDEO', 'Video'
        WHATSAPP = 'WHATSAPP', 'WhatsApp'
        ONLINE = 'ONLINE', 'Online'

    class Status(models.TextChoices):
        NEW = 'NEW', 'New'
        FOLLOWUP = 'FOLLOWUP', 'Follow-up'
        APPOINTMENT_FIXED = 'APPT_FIXED', 'Appointment Fixed'
        CONVERTED = 'CONVERTED', 'Converted to Patient'
        LOST = 'LOST', 'Lost / Not Interested'

    contact_number = models.CharField(max_length=20)
    enquiry_type = models.CharField(max_length=15, choices=EnquiryType.choices, default=EnquiryType.PHONE)
    patient_name = models.CharField(max_length=150)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Patient.Gender.choices, blank=True)
    area = models.CharField(max_length=150, blank=True)
    city_name = models.CharField(max_length=100, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    alternative_number1 = models.CharField(max_length=20, blank=True)
    alternative_number2 = models.CharField(max_length=20, blank=True)
    speaking_language = models.CharField(max_length=60, blank=True)
    patient_priority = models.CharField(max_length=10, choices=Patient.Priority.choices, blank=True)

    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='enquiries')
    appointment_date = models.DateField(null=True, blank=True)
    assign_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_enquiries', limit_choices_to={'role__in': ['DOCTOR', 'ENQ_DOCTOR']}
    )
    slot_time = models.CharField(max_length=40, blank=True)
    treatments = models.CharField(max_length=255, blank=True, default='', help_text="e.g. Vitiligo, Joint Pain")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lead_source = models.ForeignKey(LeadSource, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True)
    next_calling_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=12, choices=Status.choices, default=Status.NEW)
    converted_patient = models.OneToOneField(Patient, on_delete=models.SET_NULL, null=True, blank=True, related_name='source_enquiry')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='enquiries_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Enquiries'

    def __str__(self):
        return f"{self.patient_name} - {self.contact_number} ({self.get_status_display()})"


class CallingLog(models.Model):
    """A logged call against an enquiry or patient."""

    class CallStatus(models.TextChoices):
        ANSWERED = 'ANSWERED', 'Answered'
        NOT_ANSWERED = 'NOT_ANSWERED', 'Not Answered'
        SWITCHED_OFF = 'SWITCHED_OFF', 'Switched Off'
        BUSY = 'BUSY', 'Busy'

    class Criteria(models.TextChoices):
        GRADE_A = 'A', 'Grade A'
        GRADE_B = 'B', 'Grade B'
        GRADE_C = 'C', 'Grade C'

    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='calling_logs', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='calling_logs', null=True, blank=True)
    called_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='calls_made')
    criteria_grade = models.CharField(max_length=10, choices=Criteria.choices, blank=True)
    comments = models.TextField(blank=True)
    calling_type = models.CharField(max_length=60, blank=True, help_text="e.g. Doctor Talk Appt, Diet Counselling")
    appt_type = models.CharField(max_length=60, blank=True)
    appointment_date = models.DateTimeField(null=True, blank=True)
    call_status = models.CharField(max_length=15, choices=CallStatus.choices, default=CallStatus.ANSWERED)
    call_duration_seconds = models.PositiveIntegerField(default=0, blank=True)
    call_recording_url = models.URLField(blank=True)
    next_calling_date = models.DateField(null=True, blank=True)
    message_send_to_customer = models.BooleanField(default=False)

    # Medicine dispensing tracking captured at follow-up calls
    medicine_start_date = models.DateField(null=True, blank=True)
    medicine_end_date = models.DateField(null=True, blank=True)
    medicine_days = models.PositiveIntegerField(null=True, blank=True)
    better_patient_percent = models.PositiveIntegerField(
        null=True, blank=True, help_text="Patient's self-reported improvement, 0-100%"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def medicine_remainder_days(self):
        """Days left on the current medicine course (negative if overdue)."""
        from datetime import date
        if self.medicine_end_date:
            return (self.medicine_end_date - date.today()).days
        return None

    def __str__(self):
        who = self.patient or self.enquiry
        return f"Call to {who} by {self.called_by}"


class FollowupVisit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='followup_visits')
    visit_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visit_date']

    def __str__(self):
        return f"Followup for {self.patient.name} on {self.visit_date}"
