from .auth_urls import urlpatterns as auth_urlpatterns
from .user_urls import urlpatterns as user_urlpatterns
from .upload_document import urlpatterns as document_urlpatterns
from .biometric_urls import urlpatterns as security_urlpatterns
from .OTPVerification import urlpatterns as otpverification_urlpatterns
from .vehicle_urls import urlpatterns as vehicle_urlpatterns
from .driver_urls import urlpatterns as driver_urlpatterns
from .forget_mpin import urlpatterns as forget_urlspatterns
from .unblock_user import urlpatterns as unblock_urlspatterns
from .otpverify_forgetpassword import urlpatterns as forget_password_urlspatterns

urlpatterns = (
    auth_urlpatterns +
    user_urlpatterns +
    document_urlpatterns +
    security_urlpatterns +
    otpverification_urlpatterns+
    vehicle_urlpatterns+
    driver_urlpatterns+
    forget_urlspatterns+
    unblock_urlspatterns+
    forget_password_urlspatterns
)
