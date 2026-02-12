from urllib import response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from auth_system.models import User, Role, Password_History,User_security
from auth_system.serializer.auth import (UserRegisterSerializer,ChangePasswordSerializer,ResetPasswordSerializer)
from auth_system.utils.token_generate import token_generate
from auth_system.utils.generate_id import generate_user_id
from auth_system.utils.password import is_password_reused
from ..permission.authentication import LoginTokenAuthentication
from django.db.models import Q

# ============================================ REGISTER ========================================== #
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  

    def post(self, request, role_name):
        role_name = role_name.strip().lower()
        print("role_name",role_name)
        role = Role.objects.filter(
            name__iexact=role_name,
            is_active=True
        ).first()

        if not role:
            return Response({"success": False, "message": f"Role '{role_name}' not found"},status=status.HTTP_404_NOT_FOUND)

        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save(role=role)

        user.user_id = generate_user_id(role)
        user.save(update_fields=["user_id"])

        tokens = token_generate(user)

        return Response({
            "success": True,
            "message": f"{role.name} registered successfully",
            "data": {
                "user_id": user.user_id,
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"],
            }
        }, status=status.HTTP_201_CREATED)

# =================================================== LOGIN ============================================================ #
class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, role_name):
        data = request.data
        mobile = data.get("primary_mobile_number")
        email = data.get("email_id")
        password = data.get("password")
        mpin = data.get("mpin")
        fingerprint = data.get("fingerprint")
        facelock = data.get("facelock")
        user_id = data.get("user_id") 

        # ===== Validate at least one login method =====
        if not (password or mpin or fingerprint or facelock):
            return Response(
                {"success": False, "message": "At least one login method (password, MPIN, fingerprint, facelock) is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ===== Password login requires mobile/email =====
        if password and not (mobile or email):
            return Response(
                {"success": False, "message": "primary_mobile_number or email_id is required for password login."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ===== Fetch user =====
        user = None
        if password:
            user = User.all_objects.filter(Q(primary_mobile_number=mobile) | Q(email_id__iexact=email), is_active=True).first()
        elif mpin or fingerprint or facelock:
            if user_id:
                user = User.all_objects.filter(user_id=user_id, is_active=True).first()
            elif mobile or email:
                user = User.all_objects.filter(Q(primary_mobile_number=mobile) | Q(email_id__iexact=email), is_active=True).first()
            else:
                return Response(
                    {"success": False, "message": "user_id, email, or primary_mobile_number required for MPIN/fingerprint/facelock login."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not user:
            return Response({"success": False, "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # ===== Fetch or create User_security =====
        security, _ = User_security.objects.get_or_create(
            user=user,
            defaults={
                "is_mpin_enabled": True,
                "is_fingerprint_enabled": True,
                "is_face_lock_enabled": True,
            }
        )

        # ===== Reset all login flags =====
        security.is_mpin_enabled = False
        security.is_fingerprint_enabled = False
        security.is_face_lock_enabled = False

        # ===== Check login method =====
        if password:
            if not user.check_password(password):
                return Response({"success": False, "message": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)
            # Password login successful; no flag changes

        elif mpin:
            if not security.check_mpin(mpin):
                return Response({"success": False, "message": "Incorrect MPIN"}, status=status.HTTP_400_BAD_REQUEST)
            security.is_mpin_enabled = True

        elif fingerprint:
            security.is_fingerprint_enabled = True

        elif facelock:
            security.is_face_lock_enabled = True

        security.save()

        # ===== Role check =====
        role_name_clean = role_name.strip().lower()
        role = Role.objects.filter(name__iexact=role_name_clean, is_active=True).first()
        if not role or user.role_id != role.id:
            return Response(
                {"success": False, "message": f"User is not assigned to role '{role_name}'"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ===== Generate tokens =====
        tokens = token_generate(user)

        # ===== Return response =====
        return Response(
            {
                "success": True,
                "message": "Login successful",
                "data": {
                    "user_id": user.user_id,
                    "primary_mobile_number": user.primary_mobile_number,
                    "email_id": user.email_id,
                    "role": user.role.code if user.role else None,
                    "login_methods": {
                        "mpin": security.is_mpin_enabled,
                        "fingerprint": security.is_fingerprint_enabled,
                        "facelock": security.is_face_lock_enabled
                    },
                    "access_token": tokens["access"],
                    "refresh_token": tokens["refresh"],
                }
            },
            status=status.HTTP_200_OK
        )
# =========================================== LOGOUT ============================================ #
class LogoutAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):   
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response({"success": False, "message":" refresh_token required"}, status=400)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"success": True, "message": "Logout successful"}, status=200)
        except Exception:
            return Response({"success": False, "message": "Invalid refresh token"}, status=400)

#==================================Change Password======================================#
class ChangePasswordAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        user = request.user
        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=400)

        if is_password_reused(user, new_password):
            return Response({"error": "New password cannot match last 3 passwords"}, status=400)

        Password_History.objects.create(user=user, password=user.password)
        user.set_password(new_password)
        user.save()
  
        old_password_ids = Password_History.objects.filter(user=user).order_by('-id')[3:].values_list('id', flat=True)

        Password_History.objects.filter(id__in=old_password_ids).delete()


        return Response({"message": "Password changed successfully"}, status=200)

# ================================================ RESET PASSWORD =============================================== #
class ResetPasswordAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data.get("primary_mobile_number")
        email = serializer.validated_data.get("email_id")

        if not mobile and not email:
            return Response(
                {"success": False, "message": "primary_mobile_number or email_id required"},
                status=400
            )

        try:
            user = User.all_objects.get(
                Q(primary_mobile_number=mobile) | Q(email_id=email),
                is_active=True
            )
        except User.DoesNotExist:
            return Response(
                {"success": False, "message": "User not found"},
                status=404
            )

        return Response(
            {
                "success": True,
                "message": "User found, reset password process started"
            },
            status=200
        )

