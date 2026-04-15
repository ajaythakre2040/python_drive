from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models.mpin_history import UserMPINHistory
from auth_system.utils.mpin_crypto import encrypt_mpin
from auth_system.models import User_security, User
from auth_system.serializer import UserSecuritySerializer
from auth_system.permission.authentication import LoginTokenAuthentication
from ..utils.pagination import CustomPagination
from ..utils.sanitize import no_html_validator
from ..utils.mpin_validation import validate_mpin
 
class UserSecurityAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]

    # ================= GET ================= #
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")

        if user_id:
            try:
                user = User.objects.get(user_id=user_id)
                security = User_security.objects.get(user=user, deleted_at__isnull=True)
                serializer = UserSecuritySerializer(security)

                return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"status": False, "message": "Invalid user_id"}, status=status.HTTP_404_NOT_FOUND)
            
            except User_security.DoesNotExist:
                return Response({"status": False, "message": "User security not found"}, status=status.HTTP_404_NOT_FOUND)

        queryset = User_security.objects.filter(deleted_at__isnull=True)
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)

        serializer = UserSecuritySerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    # ================= POST (CREATE / SET MPIN) ================= #
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id") or request.data.get("user_id")
        if not user_id:
            return Response({"status": False, "message": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate user exists
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"status": False, "message": "Invalid user_id"}, status=status.HTTP_404_NOT_FOUND)

        # Get MPIN from request
        mpin = request.data.get("mpin")
        if not mpin:
            return Response({"status": False, "message": "MPIN is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate MPIN input
        try:
            mpin = no_html_validator(mpin)
            validate_mpin(mpin)
        except ValidationError as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create User_security AFTER MPIN validation
        security, created = User_security.objects.get_or_create(user=user,defaults={"created_by": request.user})

        # Check if MPIN is already set
        if security.mpin_hash not in [None, ""]:
            return Response({"status": False, "message": "MPIN already set. You cannot set it again."},status=status.HTTP_400_BAD_REQUEST)

        # Encrypt and save MPIN
        hashed_mpin = encrypt_mpin(mpin)
        security.mpin_hash = hashed_mpin
        security.is_mpin_enabled = True
        security.updated_by = request.user  # updated_by set
        security.save()

        # Update MPIN history
        mpin_history = UserMPINHistory.objects.filter(user=user).first()
        
        if not mpin_history:
            mpin_history = UserMPINHistory(user=user,mpin=hashed_mpin,created_by=request.user,updated_by=request.user)

        else:
            mpin_history.mpin = hashed_mpin
            mpin_history.updated_by = request.user
        mpin_history.save()

        return Response({"status": True, "message": "User MPIN set successfully"},status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    # ================= DELETE (SOFT DELETE) ================= #
    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id") or request.data.get("user_id")
        if not user_id:
            return Response({"status": False, "message": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user_id=user_id)
            security = User_security.objects.get(user=user, deleted_at__isnull=True)
        except (User.DoesNotExist, User_security.DoesNotExist):
            return Response({"status": False, "message": "User security not found"}, status=status.HTTP_404_NOT_FOUND)

        # Soft delete
        security.deleted_at = timezone.now()
        security.deleted_by = request.user  
        security.save()

        return Response({"status": True, "message": "User security deleted successfully"}, status=status.HTTP_200_OK)