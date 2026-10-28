#!/bin/sh
set -e
python manage.py migrate --noinput

# Optional: create the first admin from env vars (skipped if it already exists)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput \
    --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" 2>/dev/null || true
fi

exec gunicorn clinic_crm.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --timeout 60 \
  --access-logfile -
