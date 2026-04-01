import hashlib
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from auth_system.models import Login_Logout_History

class LoginTokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        jwt_auth = JWTAuthentication()

        try:
            validated = jwt_auth.authenticate(request)
        except Exception:
            raise AuthenticationFailed("Invalid or expired token")

        if validated is None:
            return None

        jwt_user, validated_token = validated  

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Authorization header missing or invalid")

        raw_token = auth_header.split(" ", 1)[1]
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        session = Login_Logout_History.objects.filter(user=jwt_user,token_hash=token_hash,logout_time__isnull=True).first()

        if not session:
            raise AuthenticationFailed("Session expired or logged out")

        if session.expires_at and session.expires_at < timezone.now():
            raise AuthenticationFailed("Session expired")

        request_ua = request.META.get("HTTP_USER_AGENT", "")
        if session.user_agent and session.user_agent != request_ua:
            raise AuthenticationFailed("Token cannot be used in a different browser/device")

        request_ip = request.META.get("REMOTE_ADDR")
        if session.ip_address and session.ip_address != request_ip:
            raise AuthenticationFailed("Token cannot be used from a different IP")
        
        return (jwt_user, validated_token)  
