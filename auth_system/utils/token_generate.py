import hashlib
from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from auth_system.models import Login_Logout_History

def token_generate(user):
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    token_hash = hashlib.sha256(access_token.encode()).hexdigest()

    expires_at = timezone.now() + timedelta(hours=2)

    Login_Logout_History.objects.create(user=user,token_hash=token_hash,expires_at=expires_at)

    return {
        "access": access_token,
        "refresh": str(refresh)
    }
