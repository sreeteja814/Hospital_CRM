import logging
import os
import requests
from django.conf import settings
from .models import NotificationLog

logger = logging.getLogger(__name__)


def _send_via_twilio(to_number, message):
    sid = os.environ.get('TWILIO_ACCOUNT_SID')
    token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_WHATSAPP_FROM')
    if not (sid and token and from_number):
        raise RuntimeError('Twilio credentials are not fully configured.')
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    resp = requests.post(url, data={'From': from_number, 'To': f"whatsapp:+{to_number.lstrip('+')}", 'Body': message}, auth=(sid, token), timeout=15)
    resp.raise_for_status()
    return resp.text


def _send_via_meta(to_number, message):
    token = os.environ.get('META_WA_TOKEN')
    phone_id = os.environ.get('META_WA_PHONE_NUMBER_ID')
    if not (token and phone_id):
        raise RuntimeError('Meta WhatsApp Cloud API credentials are not fully configured.')
    url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
    resp = requests.post(url, headers={'Authorization': f'Bearer {token}'}, json={
        'messaging_product': 'whatsapp', 'to': to_number.lstrip('+'), 'type': 'text', 'text': {'body': message},
    }, timeout=15)
    resp.raise_for_status()
    return resp.text


def send_whatsapp_message(to_number, message, patient=None, enquiry=None):
    provider = os.environ.get('WHATSAPP_PROVIDER', '').lower()
    if not to_number:
        logger.warning('send_whatsapp_message called with no recipient number; skipping.')
        return None
    log = NotificationLog(channel=NotificationLog.Channel.WHATSAPP, to_number=to_number, message=message, patient=patient, enquiry=enquiry)
    try:
        if provider == 'twilio':
            response_text = _send_via_twilio(to_number, message)
            log.status = NotificationLog.Status.SENT
            log.provider_response = response_text[:2000]
        elif provider == 'meta':
            response_text = _send_via_meta(to_number, message)
            log.status = NotificationLog.Status.SENT
            log.provider_response = response_text[:2000]
        else:
            log.status = NotificationLog.Status.LOGGED_ONLY
            if settings.DEBUG:
                logger.info("WHATSAPP (logged only) to %s: %s", to_number, message)
    except Exception as exc:
        log.status = NotificationLog.Status.FAILED
        log.provider_response = str(exc)[:2000]
        logger.exception('Failed to send WhatsApp message to %s', to_number)
    log.save()
    return log
