from django.urls import path
from auth_system.views.OTPverify_forgetpassword import VerifyOTPAndForgetPasswordAPIView

urlpatterns = [
    path('verify-otp-forget-password/', VerifyOTPAndForgetPasswordAPIView.as_view(), name='verify_otp_forget_password'),
]