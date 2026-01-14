from django.urls import path
from ..views.OTPVerification import SendOTPAPIView, VerifyOTPAPIView, ResendOTPAPIView

urlpatterns = [
    path('otp/send/', SendOTPAPIView.as_view(), name='otp-send'),
    path('otp/verify/', VerifyOTPAPIView.as_view(), name='otp-verify'),
    path('otp/resend/', ResendOTPAPIView.as_view(), name='otp-resend'),
]
