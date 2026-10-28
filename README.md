# Amritha Homeopathy — Clinic CRM

A hospital/clinic CRM built with Django for **Amritha Homeopathy Clinic and
Hospital** (Jeedimetla, Hyderabad), covering lead intake, calling logs,
appointments, doctor consultations (case sheets + prescriptions), invoicing,
HR, task management, and reports. Branding, the seeded branch record, and
opening hours (10:30 AM – 8:00 PM, all days) are already configured for this
clinic — see `patients/management/commands/seed_demo.py` and
`branches/models.py` if you add more branches later.

## Modules

| Module | What it does |
|---|---|
| **Enquiry Form** (`patients` app) | Capture a lead: contact info, treatment interest, branch, assigned doctor, lead source, next calling date |
| **Calling Logs** | Log every call against a lead or patient — status, duration, comments, next call date |
| **Patient Overview** | Confirmed patients (auto-generated Reg ID), family members, treatment history |
| **Followup Visits** | Track follow-up visits per patient |
| **Doctor Schedule / Appointments** | Book and manage appointments by date, slot, doctor, branch, status |
| **Consultation / Case Sheet** | Doctor visit notes: presenting complaints, clinical observation, progress, package duration, prescriptions |
| **Invoice / Billing** | Line-item invoices, discounts, multiple payments, balance due tracking |
| **HR** | Employee records, attendance, incentives |
| **My Task** | Simple task assignment/tracking |
| **Reports** | Appointments report, appointments slot report, doctor report, enquiry-doctor performance, employee incentive report, plus a charts dashboard |
| **Message Log** (`notifications` app) | Audit trail of WhatsApp/SMS messages the CRM has sent (or logged, if no provider is configured) |

## Access control

Every screen is now restricted by `User.role` via a `role_required(...)` decorator
(`accounts/permissions.py`) — not just the sidebar links. A non-Admin/HR user
who tries to open `/hr/` directly gets a 403 page, not just a hidden link.

| Area | Allowed roles |
|---|---|
| HR (employees, attendance) | Admin, HR |
| Invoice / Billing | Admin, Accounts, Front Desk |
| Consultation / Case Sheet (create) | Admin, Doctor, Enquiry Doctor |
| Patients, Enquiries, Callings, Followups, Appointments | Admin, Front Desk, Call Center, Doctor, Enquiry Doctor, Accounts, Pharmacy |
| Reports (general) | Admin, Front Desk, Doctor, Enquiry Doctor, Accounts, HR |
| Employee Incentive Report | Admin, HR only |
| My Task | Any logged-in user (personal task list) |

Superusers always have access everywhere. Adjust the role lists in
`accounts/models.py` (`User.HR_ROLES`, `BILLING_ROLES`, `CLINICAL_ROLES`,
`PATIENT_ROLES`, `REPORTS_ROLES`) to match how you actually want to split
access — they're plain Python lists, easy to change.

Everything is also available through the Django admin at `/admin/` for quick
bulk data management (useful for HR, lead sources, treatments, branches).
`/admin/` access is separate from these role checks — it's gated by Django's
own `is_staff`/`is_superuser` flags, so keep that limited to people who should
bypass the app's screens entirely.

## PDF documents

- **Invoice PDF** — every invoice detail page has a "Download PDF" button (`billing:invoice_pdf`), producing a clean printable invoice.
- **Prescription PDF** — every consultation/case sheet row has an "Rx PDF" button (`consultations:prescription_pdf`), producing a printable prescription with clinical observation, medicines, and follow-up date.

Both are generated server-side with `xhtml2pdf` from dedicated print templates
(`templates/billing/invoice_pdf.html`, `templates/consultations/prescription_pdf.html`)
— edit those templates to add your clinic's letterhead/logo.

## WhatsApp / SMS notifications

`notifications/services.py` has a pluggable `send_whatsapp_message()` function.
Out of the box (no credentials configured) it safely logs every message to
`NotificationLog` — viewable at **Message Log** in the sidebar, or `/admin/` —
instead of sending anything, so the app runs with zero external setup.

Hooked up already:
- **Calling Logs** — ticking "Message send to customer" sends (or logs) a WhatsApp message summarizing the call.
- **Appointment booking** — booking an appointment automatically sends (or logs) a confirmation message to the patient.

To actually send messages, set environment variables for one provider:

```bash
# Option A: Twilio WhatsApp
export WHATSAPP_PROVIDER=twilio
export TWILIO_ACCOUNT_SID=ACxxxxxxxx
export TWILIO_AUTH_TOKEN=xxxxxxxx
export TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Option B: Meta WhatsApp Cloud API
export WHATSAPP_PROVIDER=meta
export META_WA_TOKEN=xxxxxxxx
export META_WA_PHONE_NUMBER_ID=xxxxxxxx
```

No code changes needed beyond that — restart the server and messages will
actually send. Every attempt (sent, failed, or logged-only) is recorded in
`NotificationLog` for audit.

## Doctor slot auto-generation

Set each doctor's weekly availability in `/admin/` under **Appointments →
Doctor slots** (day of week, start/end time, slot length in minutes — the
`seed_demo` command creates example ones for the demo doctors). The
appointment booking form then calls `/appointments/available-slots/`
(`appointments/services.py: get_available_slots()`) via a small JS fetch and
shows clickable open-slot buttons for the chosen branch/doctor/date, already
excluding whatever's booked. Clicking a slot fills the Slot field — you can
still type a custom time if no weekly schedule is set up yet.

## Quick start (local, SQLite)

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # or use the seed command below
python manage.py seed_demo         # optional: creates demo branches/users/patients
python manage.py runserver
```

Visit http://127.0.0.1:8000/ — you'll be redirected to login.

If you ran `seed_demo`, you can log in as:

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Superuser / Admin (also `/admin/`) |
| `fdo1` | `fdo12345` | Front Desk Officer |
| `dr.demo1` | `doctor123` | Doctor |
| `dr.demo2` | `enqdoc123` | Enquiry Doctor |

**Change these passwords immediately if you deploy this anywhere real.**

## Switching to MySQL (recommended for production)

The project defaults to SQLite so it runs anywhere with zero setup. To use
MySQL instead, set these environment variables before running Django:

```bash
export USE_MYSQL=1
export DB_NAME=clinic_crm
export DB_USER=your_mysql_user
export DB_PASSWORD=your_mysql_password
export DB_HOST=127.0.0.1
export DB_PORT=3306

python manage.py migrate
python manage.py runserver
```

(On Windows, use `set VAR=value` instead of `export`.) Create the database
first: `CREATE DATABASE clinic_crm CHARACTER SET utf8mb4;`

## Project layout

```
clinic_crm/
  clinic_crm/       # settings, root urls
  accounts/         # custom User model with roles (Admin/FDO/Doctor/Enquiry Doctor/HR/Accounts/Pharmacy/Call Center)
  branches/         # multi-branch support
  patients/         # Enquiry (lead), Patient, PatientFamilyMember, CallingLog, FollowupVisit, Treatment, LeadSource
  appointments/     # DoctorSlot, Appointment
  consultations/    # Consultation (case sheet), Prescription, ConsultationDocument
  billing/          # Invoice, InvoiceItem, Payment
  hr/               # Employee, Attendance, Incentive
  tasks/            # My Task module
  reports/          # report views + dashboard
  templates/        # Bootstrap 5 based UI
```

## What to configure before going live with real patient data

Since this will hold real patient health information, at minimum before
any real deployment:

1. **Change `SECRET_KEY`** — set `DJANGO_SECRET_KEY` env var to a long random value, don't use the default.
2. **Turn off debug** — set `DJANGO_DEBUG=0` in production.
3. **Serve over HTTPS only**, and set `DJANGO_ALLOWED_HOSTS` to your real domain.
4. **Restrict admin access** — only give `is_staff`/`is_superuser` to people who truly need it; everyone else uses the app's own screens (already role-scoped by `role` on `User`).
5. **Back up the database regularly** (automated MySQL dumps or managed DB backups).
6. **Review India's Digital Personal Data Protection Act (DPDP) obligations** for storing patient health data — consent capture, data retention limits, and breach notification are all relevant for a live clinic CRM. This project doesn't implement consent tracking yet; add it before real patient onboarding if required for your setup.
7. Put this behind a real WSGI server (gunicorn/uwsgi) + nginx, not `runserver`.

## What's intentionally left as a starting point (not fully built out)

- **Excel/CSV export for reports** isn't implemented — reports are on-screen only. Adding this is a small task (e.g. `django-import-export` or a plain `csv` HttpResponse) if you need it.
- **Consent tracking for WhatsApp/SMS** isn't implemented — if you turn on real message sending, make sure you're only messaging patients who've consented, per WhatsApp Business policy and Indian telecom (TRAI) regulations around commercial messages.
- **PDF branding** — the invoice/prescription PDFs are plain — add your clinic's logo/letterhead by editing the two PDF templates directly.
- **DoctorSlot management UI** — weekly doctor schedules are currently only editable via `/admin/`, not a dedicated in-app screen.

## Branding note

This is now branded for **Amritha Homeopathy Clinic and Hospital** — it does
not use or reference "HamaraCRM" or "Dr Care Hospitals" branding from the
original reference videos (that's someone else's commercial product/brand).
If you open a second location, add it as another `Branch` in `/admin/` rather
than editing the templates — the branch's name/address/phone/hours already
render dynamically in the app footer and reports. To change the clinic
name/logo itself, edit `templates/base.html` and `templates/accounts/login.html`.
