from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password


def validate_mpin_reuse(mpin, user):
    last_three_mpins = user.mpin_histories.all()[:3]

    for old in last_three_mpins:
        if check_password(mpin, old.mpin):
            raise ValidationError("You cannot reuse your last 3 MPIN.")

    return True