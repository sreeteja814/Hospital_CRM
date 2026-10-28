from datetime import datetime, timedelta
from .models import DoctorSlot, Appointment


def _format_range(start_dt, end_dt):
    return f"{start_dt.strftime('%I:%M %p').lstrip('0')} - {end_dt.strftime('%I:%M %p').lstrip('0')}"


def get_available_slots(doctor, branch, for_date):
    if not doctor or not branch or not for_date:
        return []
    if isinstance(for_date, str):
        for_date = datetime.strptime(for_date, '%Y-%m-%d').date()
    weekday = for_date.weekday()
    defs = DoctorSlot.objects.filter(doctor=doctor, branch=branch, weekday=weekday, is_active=True)
    all_slots = []
    for d in defs:
        cursor = datetime.combine(for_date, d.start_time)
        end = datetime.combine(for_date, d.end_time)
        step = timedelta(minutes=d.slot_length_minutes or 15)
        while cursor + step <= end:
            all_slots.append(_format_range(cursor, cursor + step))
            cursor += step
    booked = set(
        Appointment.objects.filter(doctor=doctor, appointment_date=for_date)
        .exclude(status=Appointment.Status.CANCELLED)
        .values_list('slot_time', flat=True)
    )
    return [s for s in all_slots if s not in booked]
