from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from auth_system.models import OTP_verification
from ..serializer import SendOTPSerializer, VerifyOTPSerializer, RESENDOTPSerializer
from auth_system.utils.OTP import generate_otp, hash_otp, otp_expiry
from auth_system.utils.sms import send_sms
from auth_system.utils.email import send_email_otp

MAX_OTP_ATTEMPTS = 3

# ===================== SEND OTP ===================== #
class SendOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_type = serializer.validated_data["otp_type"]
        mobile_number = serializer.validated_data.get("mobile_number")
        email = serializer.validated_data.get("email")

        # Disable previous active OTPs
        OTP_verification.objects.filter(
            otp_type=otp_type,
            mobile=mobile_number if otp_type == "mobile" else None,
            email=email if otp_type == "email" else None,
            is_verified=False,
            expires_at__gt=timezone.now()
        ).update(deleted_at=timezone.now())

        otp = generate_otp()
        otp_record = OTP_verification.objects.create(
            otp_type=otp_type,
            mobile=mobile_number if otp_type == "mobile" else None,
            email=email if otp_type == "email" else None,
            otp_hash=hash_otp(otp),
            expires_at=otp_expiry(5)
        )

        if otp_type == "mobile":
            send_sms(mobile_number, otp)
        else:
            send_email_otp(email, otp)

        return Response(
            {
                "success": True,
                "message": "OTP sent successfully",
                "data": {
                    "otp_id": otp_record.id,
                    "expires_in_seconds": 300
                }
            },
            status=status.HTTP_200_OK
        )


# ===================== VERIFY OTP ===================== #
class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_id = serializer.validated_data["otp_id"]
        otp = serializer.validated_data["otp"]

        try:
            record = OTP_verification.objects.get(id=otp_id, is_verified=False, deleted_at__isnull=True)
        except OTP_verification.DoesNotExist:
            return Response({"success": False, "message": "Invalid OTP request"}, status=status.HTTP_400_BAD_REQUEST)

        if record.is_expired():
            record.deleted_at = timezone.now()
            record.save(update_fields=["deleted_at"])
            return Response({"success": False, "message": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST)

        if record.attempts >= MAX_OTP_ATTEMPTS:
            record.deleted_at = timezone.now()
            record.save(update_fields=["deleted_at"])
            return Response(
                {"success": False, "message": "Too many failed attempts. Please request new OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if record.otp_hash != hash_otp(otp):
            record.attempts += 1
            record.save(update_fields=["attempts"])
            return Response({"success": False, "message": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        record.is_verified = True
        record.deleted_at = timezone.now()
        record.save(update_fields=["is_verified", "deleted_at"])

        return Response({"success": True, "message": "OTP verified successfully"}, status=status.HTTP_200_OK)


# ===================== RESEND OTP ===================== #
class ResendOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RESENDOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp_id = serializer.validated_data["otp_id"]

        try:
            old_record = OTP_verification.objects.get(id=otp_id, is_verified=False, deleted_at__isnull=True)
        except OTP_verification.DoesNotExist:
            return Response({"success": False, "message": "OTP request not found"}, status=status.HTTP_400_BAD_REQUEST)

        old_record.deleted_at = timezone.now()
        old_record.save(update_fields=["deleted_at"])

        new_otp = generate_otp()
        new_record = OTP_verification.objects.create(
            otp_type=old_record.otp_type,
            mobile=old_record.mobile,  
            email=old_record.email,
            otp_hash=hash_otp(new_otp),
            expires_at=otp_expiry(5)
        )

        if old_record.otp_type == "mobile":
            send_sms(old_record.mobile, new_otp)
        else:
            send_email_otp(old_record.email, new_otp)

        return Response(
            {
                "success": True,
                "message": "OTP resend successfully",
                "data": {
                    "otp_id": new_record.id,
                    "expires_in_seconds": 300
                }
            },
            status=status.HTTP_200_OK
        )
