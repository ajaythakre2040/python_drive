from django.utils import timezone
from django.core.exceptions import ValidationError

MAX_ATTEMPTS = 3

def validate_attempts(mpin_history):
    """
    Check if user exceeded max attempts
    """
    if mpin_history.mpin_attempts >= MAX_ATTEMPTS:
        raise ValidationError("Too many wrong attempts. Account blocked.")
    
    return True

def increment_attempt(mpin_history):
    """
    Increase attempt count on wrong MPIN
    """
    mpin_history.mpin_attempts += 1
    mpin_history.last_attempt_at = timezone.now()
    mpin_history.save()

def reset_attempts(mpin_history):
    """
    Reset attempts after success
    """
    mpin_history.mpin_attempts = 0
    mpin_history.last_attempt_at = None
    mpin_history.save()