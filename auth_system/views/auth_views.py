from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from auth_system.models import User, Role, Password_History
from auth_system.serializer.auth import (UserRegisterSerializer,ChangePasswordSerializer,ResetPasswordSerializer)
from auth_system.utils import login_user
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

        tokens = login_user(user)

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
        mobile = request.data.get("primary_mobile_number")
        email = request.data.get("email_id")
        password = request.data.get("password")

        if not password:
            return Response({"success": False, "message": "password required"},status=status.HTTP_400_BAD_REQUEST)

        if not mobile and not email:
            return Response({"success": False,"message": "primary_mobile_number or email_id required"},status=status.HTTP_400_BAD_REQUEST)
        
        user = User.all_objects.filter(Q(primary_mobile_number=mobile) |Q(email_id__iexact=email),is_active=True).first()

        if not user:
            return Response({"success": False, "message": "User not found"},status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({"success": False, "message": "Incorrect password"},status=status.HTTP_400_BAD_REQUEST)

        role_name = role_name.strip().lower()
        role = Role.objects.filter(name__iexact=role_name, is_active=True).first()

        if not role or user.role_id != role.id:
            return Response(
                {
                    "success": False,
                    "message": f"User is not assigned to role '{role_name}'"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        tokens = login_user(user)

        return Response({
            "success": True,
            "message": "Login successful",
            "data": {
                "user_id": user.user_id,
                "primary_mobile_number": user.primary_mobile_number,
                "email_id": user.email_id,
                "role": user.role.code if user.role else None,
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"],
            }
        }, status=status.HTTP_200_OK)


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
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get mobile number or email from request
        mobile = serializer.validated_data.get("primary_mobile_number")
        email = serializer.validated_data.get("email_id")
        new_password = serializer.validated_data["new_password"]

        if not mobile and not email:
            return Response(
                {"success": False, "message": "primary_mobile_number or email_id required"},
                status=400
            )

        try:
            user = User.all_objects.get(Q(primary_mobile_number=mobile) | Q(email_id=email),is_active=True)
        except User.DoesNotExist:
            return Response({"success": False, "message": "User not found"}, status=404)

        # Check if password was reused
        if is_password_reused(user, new_password):
            return Response({"success": False, "message": "Cannot reuse last 3 passwords"}, status=400)

        # Save old password to history
        Password_History.objects.create(user=user, password=user.password)
        user.set_password(new_password)
        user.save()
       
        # Keep last 3 passwords only
        old_password_ids = Password_History.objects.filter(user=user).order_by('-id')[3:].values_list('id', flat=True)
        Password_History.objects.filter(id__in=old_password_ids).delete()

        return Response({"success": True, "message": "Password reset successfully"}, status=200)