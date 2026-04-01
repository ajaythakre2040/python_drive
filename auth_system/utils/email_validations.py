import re
from rest_framework import serializers

#==============================EMAIL VALIDATION==============================#
def check_email(email):
    email = email.strip()

    # space check
    if " " in email:
        raise serializers.ValidationError("Email cannot contain spaces")

    # first letter lowercase check
    if not email[0].islower():
        raise serializers.ValidationError("Email must start with lowercase letter")

    # regex email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        raise serializers.ValidationError("Invalid email format")

    return email  # ✅ IMPORTANT (string return)