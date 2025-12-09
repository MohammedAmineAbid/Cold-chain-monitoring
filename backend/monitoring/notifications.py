import logging
import requests
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_email_notification(subject: str, body: str, recipients: list[str]) -> None:
    if not recipients:
        return
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception:
        logger.exception("Failed to send email notification")


def send_telegram_notification(body: str) -> None:
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": settings.TELEGRAM_CHAT_ID, "text": body}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception:
        logger.exception("Failed to send Telegram notification")


def send_whatsapp_notification(body: str) -> None:
    if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_ID:
        return
    url = (
        f"https://graph.facebook.com/v17.0/{settings.WHATSAPP_PHONE_ID}/messages"
    )
    payload = {
        "messaging_product": "whatsapp",
        "to": settings.WHATSAPP_TO,
        "type": "text",
        "text": {"body": body},
    }
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        requests.post(url, json=payload, headers=headers, timeout=10)
    except Exception:
        logger.exception("Failed to send WhatsApp notification")

