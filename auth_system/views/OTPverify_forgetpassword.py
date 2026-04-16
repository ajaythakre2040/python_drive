from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db.models import Q
from auth_system.models import User, Password_History
from auth_system.models.OTPVerification import OTP_verification
from auth_system.utils.password_validation import validate_custom_password
from auth_system.utils.reused_password import is_password_reused
from auth_system.utils.OTP import hash_otp

class VerifyOTPAndForgetPasswordAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        if not otp or not new_password:
            return Response({
                "success": False,
                "message": "OTP and new_password required"
            }, status=400)

        # -------------------- Get OTP --------------------
        otp_record = OTP_verification.objects.filter(
            is_verified=False,
            deleted_at__isnull=True
        ).order_by('-id').first()

        if not otp_record:
            return Response({
                "success": False,
                "message": "OTP not found"
            }, status=400)

        # -------------------- Expiry --------------------
        if otp_record.expires_at < timezone.now():
            return Response({
                "success": False,
                "message": "OTP expired"
            }, status=400)

        # -------------------- Verify OTP --------------------
        if otp_record.otp_hash != hash_otp(otp):
            return Response({
                "success": False,
                "message": "Invalid OTP"
            }, status=400)

        # -------------------- Get User from OTP --------------------
        user = User.objects.filter(
            Q(primary_mobile_number=otp_record.mobile) |
            Q(email_id=otp_record.email)
        ).first()

        if not user:
            return Response({
                "success": False,
                "message": "User not found"
            }, status=404)

        # -------------------- Mark verified --------------------
        otp_record.is_verified = True
        otp_record.save()

        # -------------------- Password validation --------------------
        try:
            validate_custom_password(new_password)
        except Exception as e:
            return Response({
                "success": False,
                "message": str(e)
            }, status=400)

        if is_password_reused(user, new_password):
            return Response({
                "success": False,
                "message": "New password cannot match last 3 passwords"
            }, status=400)

        # -------------------- Save old password --------------------
        if user.password:
            Password_History.objects.create(user=user, password=user.password)

        # -------------------- Set new password --------------------
        user.set_password(new_password)
        user.save()

        return Response({
            "success": True,
            "message": "Password reset successful"
        }, status=200)