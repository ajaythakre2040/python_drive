from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
from ..models import User
from ..serializer.unblock_user import UserBlockHistory
from ..serializer.unblock_user import UnblockUserSerializer
from ..permission.login_attempts import reset_login_attempts
from ..permission.mpin_attempts import reset_attempts

class UnblockUserAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UnblockUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        email_id = data.get("email_id")
        primary_mobile_number = data.get("primary_mobile_number")

        if not email_id or not primary_mobile_number:
            return Response(
                {"success": False, "message": "Email and primary mobile number are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(
            Q(email_id__iexact=email_id) & Q(primary_mobile_number__iexact=primary_mobile_number)
        ).first()

        if not user:
            return Response({"success": False, "message": "User not found"}, status=404)

        # -----------------------------
        # Reset attempts if blocked
        # -----------------------------
        if user.login_attempts >= 3:
            reset_login_attempts(user)

        mpin_history = user.mpin_histories.first()
        if mpin_history and mpin_history.mpin_attempts >= 3:
            reset_attempts(mpin_history)

        # -----------------------------
        # Activate user
        # -----------------------------
        user.is_active = True
        user.save()

        # Safe created_by
        if hasattr(request, "user") and request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            created_by_user = request.user
        else:
            created_by_user = None

        # Save unblock log (without block_type)
        try:
            UserBlockHistory.objects.create(
                user=user,
                email_id=user.email_id,
                primary_mobile_number=user.primary_mobile_number,
                is_unblocked=True,created_by=created_by_user)
        
        except Exception as e:
            return Response(
                {"success": False, "message": f"Failed to log unblock: {str(e)}"},
                status=500
            )

        return Response(
            {"success": True, "message": f"User {user.email_id} unblocked successfully."},
            status=200
        )