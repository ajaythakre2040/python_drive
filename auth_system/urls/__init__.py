from .auth_urls import urlpatterns as auth_urlpatterns
from .user_urls import urlpatterns as user_urlpatterns
from .upload_document import urlpatterns as document_urlpatterns
from .biometric_urls import urlpatterns as security_urlpatterns
from .OTPVerification import urlpatterns as otpverification_urlpatterns
from .vehicle_urls import urlpatterns as vehicle_urlpatterns
from .driver_urls import urlpatterns as driver_urlpatterns

urlpatterns = (
    auth_urlpatterns +
    user_urlpatterns +
    document_urlpatterns +
    security_urlpatterns +
    otpverification_urlpatterns+
    vehicle_urlpatterns+
    driver_urlpatterns  
)
