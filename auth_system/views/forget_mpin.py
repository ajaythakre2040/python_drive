from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import UserMPINHistory
from ..models.biometric import User_security
from ..serializer.forget_mpin import ForgetMPINSerializer
from ..utils.mpin_validation import validate_mpin
from ..utils.reused_mpin import validate_mpin_reuse
from rest_framework.permissions import IsAuthenticated
from ..permission.authentication import LoginTokenAuthentication


class ForgetMPINAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ForgetMPINSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        new_mpin = serializer.validated_data["new_mpin"]

        try:
            # 🔹 Get user security
            user_security = User_security.objects.filter(user=user).first()

            if not user_security or not user_security.mpin_hash:
                return Response({"error": "MPIN not set"}, status=status.HTTP_400_BAD_REQUEST)

            # 🔐 New MPIN validation
            validate_mpin(new_mpin)
            validate_mpin_reuse(new_mpin, user)

            # ❌ Same MPIN check (IMPORTANT 🔥)
            if user_security.check_mpin(new_mpin):
                return Response(
                    {"error": "New MPIN cannot be same as old MPIN"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ✅ Save old MPIN in history
            UserMPINHistory.objects.create(
                user=user,
                mpin=user_security.mpin_hash,
                created_by=user,
                updated_by=user
            )

            # ✅ Update new MPIN
            user_security.set_mpin(new_mpin)

            return Response(
                {"message": "MPIN changed successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)