from datetime import date, timedelta, time
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from branches.models import Branch
from patients.models import LeadSource, Treatment, Patient, Enquiry, CallingLog
from appointments.models import Appointment, DoctorSlot
from consultations.models import Consultation, Prescription
from billing.models import Invoice, InvoiceItem, Payment
from hr.models import Employee
from tasks.models import Task

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo branches, users, treatments, leads, patients etc. for a quick walkthrough."

    def handle(self, *args, **options):
        # Branch — Amritha Homeopathy Clinic and Hospital, Jeedimetla, Hyderabad
        b1, _ = Branch.objects.get_or_create(
            code='AH-JEEDIMETLA',
            defaults={
                'name': 'Amritha Homeopathy - Jeedimetla',
                'city': 'Hyderabad',
                'address': 'Door no 10, 031/C5, Sri Sai Enclave Road, Meenakshi Estates, '
                            'Spring Fields Colony, Jeedimetla, Hyderabad, Telangana, 500067',
                'phone': '09885359889',
                'opening_time': time(10, 30),
                'closing_time': time(20, 0),
            }
        )

        # Users — fictional demo accounts only
        admin, created = User.objects.get_or_create(username='admin', defaults={
            'role': User.Role.ADMIN, 'is_staff': True, 'is_superuser': True, 'branch': b1,
        })
        if created:
            admin.set_password('admin123')
            admin.save()

        fdo, created = User.objects.get_or_create(username='fdo1', defaults={
            'role': User.Role.FDO, 'branch': b1, 'first_name': 'Asha', 'last_name': 'Menon',
        })
        if created:
            fdo.set_password('fdo12345')
            fdo.save()

        doc, created = User.objects.get_or_create(username='dr.demo1', defaults={
            'role': User.Role.DOCTOR, 'branch': b1, 'first_name': 'Arjun', 'last_name': 'Mehta',
        })
        if created:
            doc.set_password('doctor123')
            doc.save()

        enqdoc, created = User.objects.get_or_create(username='dr.demo2', defaults={
            'role': User.Role.ENQUIRY_DOCTOR, 'branch': b1, 'first_name': 'Nisha', 'last_name': 'Kulkarni',
        })
        if created:
            enqdoc.set_password('enqdoc123')
            enqdoc.save()

        Employee.objects.get_or_create(user=fdo, defaults={'employee_code': 'EMP001', 'branch': b1, 'date_of_joining': date(2025, 1, 10)})
        Employee.objects.get_or_create(user=doc, defaults={'employee_code': 'EMP002', 'branch': b1, 'date_of_joining': date(2024, 6, 1)})
        Employee.objects.get_or_create(user=enqdoc, defaults={'employee_code': 'EMP003', 'branch': b1, 'date_of_joining': date(2024, 9, 15)})

        # Weekly doctor availability -> feeds the auto slot suggestions on the
        # appointment booking form (Mon-Sat, morning + evening sessions).
        for weekday in range(0, 6):  # Monday=0 .. Saturday=5
            DoctorSlot.objects.get_or_create(
                doctor=doc, branch=b1, weekday=weekday,
                defaults=dict(start_time=time(9, 0), end_time=time(13, 0), slot_length_minutes=20),
            )
            DoctorSlot.objects.get_or_create(
                doctor=doc, branch=b1, weekday=weekday, start_time=time(16, 0),
                defaults=dict(end_time=time(19, 0), slot_length_minutes=20),
            )
            DoctorSlot.objects.get_or_create(
                doctor=enqdoc, branch=b1, weekday=weekday,
                defaults=dict(start_time=time(10, 0), end_time=time(13, 0), slot_length_minutes=15),
            )

        # Lead sources & treatments
        for name in ['Facebook', 'Google Maps', 'Just Dial', 'Employee Referral', 'Instagram', 'Walk-in']:
            LeadSource.objects.get_or_create(name=name)

        treatments = {}
        for name, fee in [('Psoriasis', 800), ('Vitiligo', 800), ('Acne / Pimples', 600), ('Pigmentation', 700), ('Hair Fall', 600)]:
            t, _ = Treatment.objects.get_or_create(name=name, defaults={'default_consultation_fee': fee})
            treatments[name] = t

        # A sample enquiry (lead) — fictional demo patient
        enquiry, _ = Enquiry.objects.get_or_create(
            contact_number='9000000001',
            defaults=dict(
                patient_name='Demo Enquiry Patient', age=34, gender='M', city_name='Hyderabad',
                whatsapp_number='9000000001', speaking_language='Telugu, English',
                patient_priority=Patient.Priority.HIGH, branch=b1, appointment_date=date.today() + timedelta(days=1),
                assign_doctor=enqdoc, slot_time='10:30 AM', consultation_fee=800,
                lead_source=LeadSource.objects.get(name='Google Maps'),
                remarks='Interested in psoriasis treatment package.', next_calling_date=date.today() + timedelta(days=2),
                created_by=fdo,
            )
        )
        enquiry.treatments.add(treatments['Psoriasis'])

        CallingLog.objects.get_or_create(
            enquiry=enquiry, called_by=fdo, defaults=dict(
                criteria_grade='A', comments='Spoke to patient, advised to continue with medicines.',
                calling_type='Doctor Talk Appt', call_status=CallingLog.CallStatus.ANSWERED,
                call_duration_seconds=185, next_calling_date=date.today() + timedelta(days=5),
            )
        )

        # A converted patient with full history — fictional demo patient
        patient, created = Patient.objects.get_or_create(
            mobile_number='9000000002',
            defaults=dict(
                name='Demo Patient Example', age=29, gender='F', city='Hyderabad', area='Suchitra',
                whatsapp_number='9000000002', priority=Patient.Priority.MEDIUM, branch=b1,
                lead_source=LeadSource.objects.get(name='Instagram'), assigned_doctor=doc, created_by=fdo,
            )
        )
        if created:
            patient.treatments.add(treatments['Vitiligo'])

        appt, _ = Appointment.objects.get_or_create(
            patient=patient, appointment_date=date.today(), defaults=dict(
                branch=b1, doctor=doc, treatment=treatments['Vitiligo'], appt_type=Appointment.ApptType.FOLLOW_UP,
                slot_time='11:00 AM - 11:20 AM', status=Appointment.Status.VISITED, payment_due=0, created_by=fdo,
            )
        )

        consultation, created = Consultation.objects.get_or_create(
            patient=patient, consulted_date=date.today(), defaults=dict(
                appointment=appt, doctor=doc, treatment=treatments['Vitiligo'],
                presenting_complaints='White patches on hands, gradually spreading over 6 months.',
                personal_history='No known allergies. No family history reported.',
                clinical_observation='Depigmented patches on dorsum of both hands. Advised to continue topical treatment.',
                progress='Improving', suggested_duration='3 months', package_duration='3/M',
                package_end_date=date.today() + timedelta(days=90), medicine_days=30,
                followup_date=date.today() + timedelta(days=30),
                patient_status=Consultation.PatientStatus.CONTINUE_MEDICINE,
            )
        )
        if created:
            Prescription.objects.create(consultation=consultation, medicine_name='Tacrolimus Ointment 0.1%', dosage='Apply twice daily', duration_days=30)
            Prescription.objects.create(consultation=consultation, medicine_name='Vitamin D3 Tablets', dosage='1-0-0 after food', duration_days=30)

        invoice, created = Invoice.objects.get_or_create(
            patient=patient, invoice_date=date.today(), branch=b1, defaults=dict(
                payment_mode=Invoice.PaymentMode.UPI, status=Invoice.Status.PARTIAL, created_by=fdo,
            )
        )
        if created:
            InvoiceItem.objects.create(invoice=invoice, description='Consultation Fee', quantity=1, unit_price=800)
            InvoiceItem.objects.create(invoice=invoice, description='Vitiligo Treatment Package (Month 1)', quantity=1, unit_price=4500)
            Payment.objects.create(invoice=invoice, amount=2000, paid_on=date.today(), mode=Invoice.PaymentMode.UPI, received_by=fdo)

        Task.objects.get_or_create(
            title='Call Demo Patient Example to confirm next follow-up', assigned_to=fdo, defaults=dict(
                assigned_by=doc, due_date=date.today() + timedelta(days=1), priority=Task.Priority.MEDIUM,
            )
        )

        self.stdout.write(self.style.SUCCESS(
            "Demo data seeded.\n"
            "Logins -> admin/admin123 (superuser), fdo1/fdo12345 (Front Desk), "
            "dr.demo1/doctor123 (Doctor), dr.demo2/enqdoc123 (Enquiry Doctor)"
        ))
