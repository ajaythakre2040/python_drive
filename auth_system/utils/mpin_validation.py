from django.core.exceptions import ValidationError

COMMON_MPINS = ["0000", "1111", "1234", "4321"]

def validate_mpin(mpin: str):
    # ✅ Numeric check
    if not mpin.isdigit():
        raise ValidationError("MPIN must be digits only.")

    # ✅ Length check
    if len(mpin) != 4:
        raise ValidationError("MPIN must be 4 digits.")

    # ✅ Common MPIN block
    if mpin in COMMON_MPINS:
        raise ValidationError("MPIN is too weak.")

    # ✅ All same digits (1111)
    if len(set(mpin)) == 1:
        raise ValidationError("MPIN cannot be same digits.")

    # ✅ Simple sequential check (1234 / 4321)
    if mpin in "0123456789" or mpin in "9876543210":
        raise ValidationError("MPIN cannot be sequential.")

    return True