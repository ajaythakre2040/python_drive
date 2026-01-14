import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


def send_email_otp(email: str, otp: str) -> bool:
    subject = "YOUR OTP VERIFICATION CODE"
    message = f"Your OTP is {otp}. It is valid for 5 minutes."

    logger.info("[Email] Sending OTP to %s", email)
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info("[Email] Sent OTP to %s", email)
        return True
    except Exception:
        logger.exception("Failed to send OTP email to %s", email)
        return False    