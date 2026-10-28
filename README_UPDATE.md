# Amritha Homeopathy CRM — Major Update

This is a big update covering everything found after a thorough re-review of your
4 reference videos. Read this whole file before applying anything.

## What's new

- **Package/Registration billing model** on Patient: registration date, package
  amount, duration (months), registration end date, renewal date, paid/due/refund
  amounts, consult fee, cheque stop/bounce flag.
- **Multiple staff "ownership" roles** per patient: Unit Doctor, Senior Doctor,
  Renewal Doctor, Enquiry Ownership, Unit Ownership, CRO Name, Patient Reg By.
- **Full address details**: Country, State, PinCode, Address, Email, Marital
  Status, Source of Information — plus a separate **Courier Address** section
  for mailing medicines.
- **Medicine dispensing tracking** on Calling Logs: Medicine Start/End Date,
  Medicine Days, and an auto-calculated **Medicine Remainder Days** countdown.
- **"Better Patient %"** — self-reported improvement percentage, captured per call.
- **Patient Referral tracking** — log a referred mobile number against a patient.
- **Patient Complaints log** — separate from clinical notes.
- **Full homeopathy clinical documentation** on Consultations: BP, Pulse,
  Weight, Height, Temperature, BMI, Miasmatic Diagnosis, Repertorial Result,
  Mental/Physical General, Management, Diet, Exercises, Nutrition, Present
  Medication, Level of Assurance, Criteria/Future Plan of Rx, DOs and DON'Ts.
- **Receipt/cheque-level payment detail** on Invoices: Manual Receipt No,
  Cheque No, Cheque Status, Cheque Date.
- **New reports**: Doctor Appointments Report, Enquiry Doctor Inactive
  Patients Report, Enquiry Doctor Ownership Report, Unit Doctor Ownership
  Report, Medicine Calling Report, and a Followup Calling Report under a new
  **Master** menu.
- Reports are now grouped into a dropdown in the navbar (too many to list flat).

## IMPORTANT — how to apply this safely to your real project

Your live database already has real patients (Teja, etc.) and its own migration
history. This update is designed to be layered on top of that safely, but
follow these steps exactly, in order:

### 1. Back up first (takes 10 seconds, non-negotiable for a change this size)

In your project folder (where `db.sqlite3` lives):
```powershell
copy db.sqlite3 db.sqlite3.backup
```
If anything goes wrong, you can always stop, delete the broken `db.sqlite3`,
and rename `db.sqlite3.backup` back to `db.sqlite3` to get back to exactly
where you are right now.

### 2. What to copy from this zip, and what NOT to

**Copy and overwrite these from the zip:**
- Every `.py` file inside `accounts/`, `branches/`, `patients/`, `appointments/`,
  `consultations/`, `billing/`, `hr/`, `tasks/`, `notifications/`, `reports/`
  (models.py, views.py, forms.py, urls.py, admin.py — whichever exist in each)
- `templates/base.html`
- Every file under `templates/patients/`, `templates/consultations/`,
  `templates/appointments/`, `templates/billing/`, `templates/accounts/`,
  `templates/reports/`

**Do NOT copy these — leave your existing ones alone:**
- Any `migrations/` folder (this zip doesn't include any — your existing
  migration history must stay exactly as it is)
- `static/images/logo.jpg` (your real logo — not included here)
- `db.sqlite3` (your real data)
- `templates/accounts/login.html` (only if you've customized it beyond what
  we set up together — otherwise fine to overwrite, it's unchanged)

If you're not sure whether a specific file changed, safest is to just
overwrite everything *except* the four items above — every `.py` file in this
zip is a complete, correct replacement for its counterpart in your project.

### 3. Apply the database changes

After copying the files above:
```powershell
python manage.py makemigrations
python manage.py migrate
```
This will detect all the new fields/models and generate the migration for
you automatically — same as every other field we've added so far today. It
will NOT touch or delete any existing patient data; new fields just start
blank until you fill them in.

### 4. Test it

Log in, open an existing patient (Teja), and confirm:
- Their name/mobile/history is all still there, untouched
- You now see new sections for Registration/Package, Staff Ownership,
  Referrals, Complaints
- Try New Consultation and confirm the new homeopathy fields show up
- Check the Reports dropdown and the new **Master** menu

### 5. If something breaks

Stop the server, restore your backup:
```powershell
del db.sqlite3
ren db.sqlite3.backup db.sqlite3
```
Then tell me exactly what error you saw and I'll fix it — same as we've done
all day.

## Still not built (flagging honestly)

- The "Personal History" sub-fields in the homeopathy case-taking were too
  blurry in the video for me to read reliably, so that section stays as one
  free-text box rather than the individual categorized fields the reference
  system seems to have.
- The in-consultation "Send Message" feature and the stepper-style call-stage
  icons weren't built — these seemed lower priority than the clinical/billing
  fields. Say the word if you want these too.
