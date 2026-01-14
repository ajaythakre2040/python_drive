from auth_system.models import User

def generate_user_id(role):

    prefix = role.code.upper()
    last_user = (User.objects.filter(role=role, user_id__startswith=prefix).order_by("id").last())

    if last_user and last_user.user_id:
        try:
            last_number = int(last_user.user_id.replace(prefix, ""))
        except ValueError:
            last_number = 0
    else:
        last_number = 0

    new_number = last_number + 1

    return f"{prefix}{new_number:04d}"
