from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..models import UserMPINHistory, User
from ..models.biometric import User_security
from ..serializer.forget_mpin import ForgetMPINSerializer
from ..utils.reused_mpin import validate_mpin_reuse
from ..permission.authentication import LoginTokenAuthentication


class ForgetMPINAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ForgetMPINSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        request_user = request.user
        user_id = serializer.validated_data["user_id"]
        new_mpin = serializer.validated_data["new_mpin"]

        try:
            # 🔹 Fetch user from DB
            user = User.all_objects.filter(user_id=user_id).first()
            if not user:
                return Response(
                    {"success": False, "message": "Invalid user_id"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # 🔐 SECURITY CHECK (VERY IMPORTANT)
            if user.id != request_user.id:
                return Response(
                    {"success": False, "message": "You are not allowed to change another user's MPIN"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 🔹 Get user security
            user_security = User_security.objects.filter(user=user).first()

            if not user_security or not user_security.mpin_hash:
                return Response(
                    {"success": False, "message": "MPIN not set"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 🔐 Reuse check
            validate_mpin_reuse(new_mpin, user)

            # ❌ Same MPIN check
            if user_security.check_mpin(new_mpin):
                return Response(
                    {"success": False, "message": "New MPIN cannot be same as old MPIN"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ Save old MPIN in history
            UserMPINHistory.objects.create(
                user=user,
                mpin=user_security.mpin_hash,
                created_by=request_user,
                updated_by=request_user
            )

            # ✅ Update new MPIN
            user_security.set_mpin(new_mpin)

            return Response(
                {
                    "success": True,
                    "message": "MPIN changed successfully",
                    "data": {
                        "user_id": user.user_id
                    }
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )