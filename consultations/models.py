from django.conf import settings
from django.db import models
from patients.models import Patient, Treatment
from appointments.models import Appointment


class Consultation(models.Model):
    """A single doctor visit / 'Case Sheet' entry for a patient."""

    class PatientStatus(models.TextChoices):
        RECOMMENDED_FOR_EXERCISE = 'REC_EXERCISE', 'Recommended For Exercise'
        CONTINUE_MEDICINE = 'CONTINUE_MEDICINE', 'Continue Medicine'
        REVIEW_NEEDED = 'REVIEW_NEEDED', 'Review Needed'
        DISCHARGED = 'DISCHARGED', 'Discharged'
        CURED = 'CURED', 'Cured'

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultations')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultations_done')
    treatment = models.ForeignKey(Treatment, on_delete=models.SET_NULL, null=True, blank=True)
    consulted_date = models.DateField()

    # --- Preliminary Data ---
    presenting_complaints = models.TextField(blank=True)
    personal_history = models.TextField(blank=True, help_text="Appetite, bowels, sleep, thirst, thermals, etc.")

    # --- Vitals / General Examination ---
    bp = models.CharField(max_length=20, blank=True, verbose_name='BP')
    pulse = models.CharField(max_length=20, blank=True)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Weight (KG)')
    height_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name='Height (CM)')
    temperature = models.CharField(max_length=20, blank=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='BMI')
    systemic_examination = models.TextField(blank=True, verbose_name='Systemic Examination (O/E)')

    # --- Homeopathic case-taking / diagnosis ---
    particular = models.TextField(blank=True, help_text="Particular symptoms")
    mental_general = models.TextField(blank=True)
    physical_general = models.TextField(blank=True)
    miasmatic_diagnosis = models.CharField(max_length=255, blank=True)
    repertorial_result = models.TextField(blank=True)
    analysis_evaluation = models.TextField(blank=True, verbose_name='Analysis & Evaluation and Repertorial Totality')

    # --- Plan ---
    management = models.TextField(blank=True)
    diet = models.TextField(blank=True)
    exercises = models.TextField(blank=True)
    nutrition = models.CharField(max_length=100, blank=True)
    present_medication = models.TextField(blank=True)
    level_of_assurance = models.CharField(max_length=100, blank=True)
    criteria_future_plan_rx = models.TextField(blank=True, verbose_name='Criteria / Future Plan of Rx')
    dos_and_donts = models.TextField(blank=True, verbose_name="DOs and DON'Ts")

    # --- Clinical Observation section (existing) ---
    clinical_observation = models.TextField(blank=True)
    progress = models.CharField(max_length=255, blank=True)
    suggested_duration = models.CharField(max_length=100, blank=True)
    package_duration = models.CharField(max_length=50, blank=True, help_text="e.g. 3/M")
    package_end_date = models.DateField(null=True, blank=True)

    medicine_days = models.PositiveIntegerField(null=True, blank=True)
    followup_date = models.DateField(null=True, blank=True)
    patient_status = models.CharField(max_length=20, choices=PatientStatus.choices, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-consulted_date', '-created_at']

    def __str__(self):
        return f"{self.patient.name} - {self.consulted_date} ({self.doctor})"


class ConsultationDocument(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='consultation_docs/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    medicine_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=100, blank=True, help_text="e.g. 1-0-1 after food")
    duration_days = models.PositiveIntegerField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.medicine_name} ({self.consultation.patient.name})"


class ConsultationMessage(models.Model):
    """A message logged against a consultation (mirrors the reference's in-consultation
    'Send Message' log — who sent what, from which designation)."""
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='messages')
    from_designation = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message on {self.consultation} at {self.created_at:%d-%m-%Y}"
