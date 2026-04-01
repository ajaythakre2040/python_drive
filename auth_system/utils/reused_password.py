from django.contrib.auth.hashers import check_password
from ..models.password_history import Password_History

def is_password_reused(user, new_password, limit=3):
    last_passwords = Password_History.objects.filter(user=user).order_by('-id')[:limit]

    for history in last_passwords:
        if check_password(new_password, history.password):
            return True  

    return False  
