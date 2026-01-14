from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from auth_system.models import User_security, User
from auth_system.serializer import UserSecuritySerializer
from auth_system.permission.authentication import LoginTokenAuthentication
from ..utils.pagination import CustomPagination
from ..utils.sanitize import no_html_validator

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

    # ================= POST (CREATE / UPDATE) ================= #
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id") or request.data.get("user_id")
        if not user_id:
            return Response({"status": False, "message": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"status": False, "message": "Invalid user_id"}, status=status.HTTP_404_NOT_FOUND)

        security, created = User_security.objects.get_or_create(user=user, defaults={"created_by": request.user})

        # ===== MPIN =====
        mpin = request.data.get("mpin")
        if mpin:
            try:
                mpin = no_html_validator(mpin)
            except Exception as e:
                return Response({"status": False, "message": str(e)}, status=400)
            if len(mpin) != 4 or not mpin.isdigit():
                return Response({"status": False, "message": "MPIN must be exactly 4 digits"}, status=400)
            security.mpin_hash = make_password(mpin)
            security.is_mpin_enabled = True

        # ===== Fingerprint =====
        fingerprint = request.data.get("fingerprint")
        if fingerprint:
            try:
                fingerprint = no_html_validator(fingerprint)
            except Exception as e:
                return Response({"status": False, "message": str(e)}, status=400)
            security.fingerprint = make_password(fingerprint)
            security.is_fingerprint_enabled = True

        # ===== Face Lock =====
        face_device_id = request.data.get("face_device_id")
        if face_device_id:
            try:
                face_device_id = no_html_validator(face_device_id)
            except Exception as e:
                return Response({"status": False, "message": str(e)}, status=400)
            security.faceLock = make_password(face_device_id)
            security.is_face_lock_enabled = True

        security.save()
        return Response({"status": True, "message": "User security saved successfully"}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    # ================= PATCH (UPDATE) ================= #
    def patch(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id") or request.data.get("user_id")
        if not user_id:
            return Response({"status": False, "message": "user_id is required"}, status=400)

        try:
            user = User.objects.get(user_id=user_id)
            security = User_security.objects.get(user=user, deleted_at__isnull=True)
        except (User.DoesNotExist, User_security.DoesNotExist):
            return Response({"status": False, "message": "User security not found"}, status=404)

        # ===== MPIN UPDATE =====
        if "mpin" in request.data:
            mpin = request.data.get("mpin")
            try:
                mpin = no_html_validator(mpin)
            except Exception as e:
                return Response({"status": False, "message": str(e)}, status=400)
            if len(mpin) != 4 or not mpin.isdigit():
                return Response({"status": False, "message": "MPIN must be exactly 4 digits"}, status=400)
            security.mpin_hash = make_password(mpin)
            security.is_mpin_enabled = True

        # ===== MPIN ENABLE / DISABLE =====
        if "is_mpin_enabled" in request.data:
            security.is_mpin_enabled = bool(request.data["is_mpin_enabled"])
            if not security.is_mpin_enabled:
                security.mpin_hash = None

        # ===== Fingerprint ENABLE / DISABLE =====
        if "is_fingerprint_enabled" in request.data:
            security.is_fingerprint_enabled = bool(request.data["is_fingerprint_enabled"])
            if not security.is_fingerprint_enabled:
                security.fingerprint = None

        # ===== Face Lock ENABLE / DISABLE =====
        if "is_face_lock_enabled" in request.data:
            security.is_face_lock_enabled = bool(request.data["is_face_lock_enabled"])
            if not security.is_face_lock_enabled:
                security.faceLock = None

        security.updated_by = request.user
        security.save()
        return Response({"status": True, "message": "User security updated successfully"}, status=200)

    # ================= DELETE (SOFT DELETE) ================= #
    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id") or request.data.get("user_id")
        if not user_id:
            return Response({"status": False, "message": "user_id is required"}, status=400)

        try:
            user = User.objects.get(user_id=user_id)
            security = User_security.objects.get(user=user, deleted_at__isnull=True)
        except (User.DoesNotExist, User_security.DoesNotExist):
            return Response({"status": False, "message": "User security not found"}, status=404)

        security.deleted_at = timezone.now()
        security.deleted_by = request.user
        security.save()
        return Response({"status": True, "message": "User security deleted successfully"}, status=200)
