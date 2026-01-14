import logging

logger = logging.getLogger(__name__)


def send_sms(mobile: str, otp: str) -> bool:
    try:
        logger.info("[SMS] OTP sent to %s: %s", mobile, otp)
        return True
    except Exception:
        logger.exception("Failed to send OTP to %s", mobile)
        return False
    