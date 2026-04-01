from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from auth_system.models import User, Role, Password_History,User_security
from auth_system.serializer.auth import (UserRegisterSerializer,ChangePasswordSerializer,ResetPasswordSerializer)
from auth_system.utils.token_generate import token_generate
from auth_system.utils.generate_id import generate_user_id
from auth_system.utils.reused_password import is_password_reused
from ..permission.authentication import LoginTokenAuthentication
from ..permission.mpin_attempts import validate_attempts, increment_attempt, reset_attempts
from django.db.models import Q
from django.db import IntegrityError
from auth_system.models.mpin_history import UserMPINHistory
from django.conf import settings
from auth_system.models.change_reset_password import Password_Action_Log
from auth_system.models.login_logout_history import Login_Logout_History
from auth_system.permission.login_attempts import check_login_attempts,register_failed_attempt,reset_login_attempts

# ============================================ REGISTER ========================================== #
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, role_name):
        role_name = role_name.strip().lower()

        # Get role from URL
        role = Role.objects.filter(
            name__iexact=role_name,
            is_active=True
        ).first()
        if not role:
            return Response({"success": False, "message": f"Role '{role_name}' not found"},
                            status=status.HTTP_404_NOT_FOUND)

        # Pass role to serializer context
        serializer = UserRegisterSerializer(data=request.data, context={"role": role})
        serializer.is_valid(raise_exception=True)

        try:
            user = serializer.save()
            user.user_id = generate_user_id(role)
            user.save(update_fields=["user_id"])
        except IntegrityError:
            return Response({"success": False, "message": "Duplicate user data, try again."},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "success": True,
            "message": f"{role.name} registered successfully",
            "data": {"user_id": user.user_id}
        }, status=status.HTTP_201_CREATED)

# =================================================== LOGIN ============================================================ #
MAX_PASSWORD_ATTEMPTS = 3
MAX_MPIN_ATTEMPTS = 3

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

        # ----------------------------- Validate login method -----------------------------
        if not (password or mpin or fingerprint or facelock):
            return Response({"success": False, "message": "At least one login method required"}, status=status.HTTP_400_BAD_REQUEST)

        if password and not (mobile or email):
            return Response({"success": False, "message": "Mobile or Email required for password login"}, status=status.HTTP_400_BAD_REQUEST)

        # ----------------------------- Fetch user -----------------------------
        user = None
        if user_id:
            user = User.all_objects.filter(user_id=user_id).first()
        elif mobile or email:
            user = User.all_objects.filter(Q(primary_mobile_number=mobile) | Q(email_id__iexact=email)).first()

        if not user:
            return Response({"success": False, "message": "User not found"}, status=status.HTTP_403_FORBIDDEN)

        # ----------------------------- User security & MPIN history -----------------------------
        security, _ = User_security.objects.get_or_create(user=user)
        mpin_history = user.mpin_histories.first()
        if not mpin_history:
            mpin_history = UserMPINHistory.objects.create(user=user)

        # ----------------------------- Check both blocks -----------------------------
        if user.login_attempts >= MAX_PASSWORD_ATTEMPTS:
            return Response({"success": False, "message": "User blocked due to multiple wrong password attempts. Please unblock."}, status=403)

        try:
            validate_attempts(mpin_history)  
        except Exception:
            return Response({"success": False, "message": "User blocked due to multiple wrong MPIN attempts. Please unblock."}, status=403)

        login_method = None

        # ----------------------------- PASSWORD LOGIN -----------------------------
        if password:
            if not user.check_password(password):
                register_failed_attempt(user)
                return Response({"success": False, "message": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)
            reset_login_attempts(user)
            login_method = "password"

        # ----------------------------- MPIN LOGIN -----------------------------
        elif mpin:
            if not security.check_mpin(mpin):
                increment_attempt(mpin_history)
                return Response({"success": False, "message": "Incorrect MPIN"}, status=status.HTTP_400_BAD_REQUEST)
            reset_attempts(mpin_history)
            login_method = "mpin"

        # ----------------------------- FINGERPRINT LOGIN -----------------------------
        elif fingerprint:
            if not security.is_fingerprint_enabled:
                return Response({"success": False, "message": "Fingerprint login disabled"}, status=status.HTTP_400_BAD_REQUEST)
            login_method = "fingerprint"

        # ----------------------------- FACELOCK LOGIN -----------------------------
        elif facelock:
            if not security.is_face_lock_enabled:
                return Response({"success": False, "message": "FaceLock login disabled"}, status=status.HTTP_400_BAD_REQUEST)
            login_method = "facelock"

        # ----------------------------- ROLE CHECK -----------------------------
        role = Role.objects.filter(name__iexact=role_name.strip(), is_active=True).first()
        if not role or user.role_id != role.id:
            return Response({"success": False, "message": "Invalid role"}, status=403)

        # ----------------------------- ACTIVE SESSION CHECK -----------------------------
        if not getattr(settings, "ALLOW_MULTIPLE_SESSIONS", False):
            active_session = Login_Logout_History.objects.filter(user=user, logout_time__isnull=True).first()
            if active_session:
                if timezone.now() < active_session.expires_at:
                    return Response({"success": False, "message": "Already logged in"}, status=status.HTTP_403_FORBIDDEN)
                else:
                    active_session.logout_time = active_session.expires_at
                    active_session.is_active = False
                    active_session.save()

        # ----------------------------- TOKEN GENERATE -----------------------------
        try:
            tokens = token_generate(user, request)
        except IntegrityError:
            return Response({"success": False, "message": "Token generation failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # ----------------------------- SUCCESS RESPONSE -----------------------------
        return Response({
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"],
                "login_method": login_method
            }
        }, status=200)
    
# =========================================== LOGOUT ============================================ #
class LogoutAPIView(APIView):
    permission_classes=[IsAuthenticated]
    authentication_classes=[LoginTokenAuthentication]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"success":False,"message":"refresh_token required"},status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            try:
                
                Login_Logout_History.objects.filter(user=request.user,logout_time__isnull=True).update(logout_time=timezone.now(), is_active=False)
            except Exception:
                pass

            token.blacklist()
            return Response({"success":True, "message":"Logout successfully"},status=status.HTTP_200_OK)
        except Exception:
            return Response({"success":False , "message":"Invalid refresh token"},status=status.HTTP_400_BAD_REQUEST)
        

#=====================================Forced-Logout=======================================#
class ForceLogoutAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")

        if not username:
            return Response(
                {"success": False, "message": "Username required"},status=status.HTTP_400_BAD_REQUEST)

        # ---------------------- Fetch user ----------------------
        user = None
        if username.isdigit() and len(username) == 10:
            user = User.objects.filter(primary_mobile_number=username).first()
        elif "@" in username and "." in username:
            user = User.objects.filter(email_id__iexact=username).first()
        else:
            return Response(
                {"success": False, "message": "Invalid username. Use email or primary mobile number."},status=status.HTTP_400_BAD_REQUEST)

        if not user:
            return Response({"success": False, "message": "User not found"},status=status.HTTP_404_NOT_FOUND)

        # ---------------------- Active sessions ----------------------
        sessions = Login_Logout_History.objects.filter(user=user,is_active=True)

        if not sessions.exists():
            return Response({"success": True, "message": "No active sessions found"},status=status.HTTP_200_OK)

        # ---------------------- Force logout ----------------------
        for session in sessions:
            # JWT token blacklist attempt
            try:
                token = RefreshToken(session.token_hash)
                token.blacklist()
            except Exception:
                pass

            session.logout_time = timezone.now()
            session.is_active = False
            session.concurrent_info = {
                "type": "force_logout",
                "ip_address": request.META.get("REMOTE_ADDR", ""),
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                "time": str(timezone.now())
            }
            session.save(update_fields=["logout_time", "is_active", "concurrent_info"])

        return Response({"success": True, "message": "Previous device logged out successfully"},status=status.HTTP_200_OK)

#==================================Change Password======================================#
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [LoginTokenAuthentication]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data,context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        # ✅ Check old password
        if not user.check_password(old_password):
            return Response({"success": False, "message": "Old password is incorrect"},status=status.HTTP_400_BAD_REQUEST)

        # ✅ Prevent same password
        if user.check_password(new_password):
            return Response({"success": False, "message": "New password cannot be same as current password"},status=status.HTTP_400_BAD_REQUEST)

        # ✅ Prevent reuse (last 3 passwords)
        if is_password_reused(user, new_password):
            return Response({"success": False, "message": "New password cannot be same as last 3 passwords"},status=status.HTTP_400_BAD_REQUEST)

        # ✅ Save current password to history
        Password_History.objects.create(user=user,password=user.password)

        # ✅ Update password
        user.set_password(new_password)
        user.save()

        # ✅ Log action
        try:
            Password_Action_Log.objects.create(user=user,action_by=user,action_type="change",action_count=1)
        
        except Exception as e:
            print("Password log error:", e)

        # ✅ Keep only last 3 passwords
        old_ids = Password_History.objects.filter(user=user).order_by('-id')[3:].values_list('id', flat=True)

        if old_ids:
            Password_History.objects.filter(id__in=old_ids).delete()

        return Response({"success": True, "message": "Password changed successfully"},status=status.HTTP_200_OK)
    
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