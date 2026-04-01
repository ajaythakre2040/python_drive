from django.core.exceptions import ValidationError
from datetime import date

def validate_full_name(name):
    if len(name.strip()) < 3:
        raise ValidationError("Full name must be at least 3 characters.")
    return name.strip()

def validate_mobile_number(mobile):
    if not mobile:
        return mobile

    if not mobile.isdigit() or len(mobile) != 10:
        raise ValidationError("Mobile number must be 10 digits.")
    
    if len(mobile) != 10:
        raise ValidationError("Mobile number must be exactly 10 digits.")

    if mobile[0] not in ["6", "7", "8", "9"]:
        raise ValidationError("Mobile must start with 6, 7, 8, or 9.")

    return mobile

def validate_dob(dob):
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    if age < 18:
        raise ValidationError("User must be at least 18 years old.")

    if age > 100:
        raise ValidationError("Age cannot be more than 100.")

    return dob