import random 
import hashlib
from django.utils import timezone
from datetime import timedelta

def generate_otp():
    return str(random.randint(100000,999999))

def hash_otp(otp:str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()

def otp_expiry(minutes=5):
    return timezone.now() + timedelta(minutes=minutes)

