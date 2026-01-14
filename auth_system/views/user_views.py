from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from ..permission.authentication import LoginTokenAuthentication
from auth_system.models import User
from auth_system.serializer import UserSerializer
from ..utils.pagination import CustomPagination
from ..utils.sanitize import no_html_validator

SANITIZE_FIELDS = ["full_name","email_id", "current_address","permanent_address",]

class UserAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]  

    # =============================================== GET / GET BY ID ==============================================#
    def get(self, request, id=None):
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "You are logged out. Please login first"},status=status.HTTP_401_UNAUTHORIZED)
        try:
            if id:
                user = User.objects.get(id=id, deleted_at__isnull=True)
                serializer = UserSerializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)

            users = User.objects.filter(deleted_at__isnull=True)
            paginator = CustomPagination()
            paginated_queryset = paginator.paginate_queryset(users, request, view=self)
            serializer = UserSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Something went wrong: {str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ====================================== POST ========================================== #
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "You are logged out. Please login first"},status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        for field in SANITIZE_FIELDS:
            if field in data and data[field]:
                try:
                    data[field] = no_html_validator(data[field])
                except Exception as e:
                    return Response({"error": f"Invalid input in {field}: {str(e)}"},status=status.HTTP_400_BAD_REQUEST)

        phone = data.get("phone") or data.get("mobile_number")
        if not phone:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(phone) != 10 or not phone.isdigit():
            return Response({"error": "Phone number must be exactly 10 digits"},status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ================================== PATCH / UPDATE ======================================== #
    def patch(self, request, id):
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "You are logged out. Please login first"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = User.objects.get(id=id, deleted_at__isnull=True)
        except User.DoesNotExist:
            return Response({"error": "User not found to update"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        for field in SANITIZE_FIELDS:
            if field in data and data[field]:
                try:
                    data[field] = no_html_validator(data[field])
                except Exception as e:
                    return Response({"error": f"Invalid input in {field}: {str(e)}"},status=status.HTTP_400_BAD_REQUEST)

        phone = data.get("phone") or data.get("mobile_number")
        if phone and (len(phone) != 10 or not phone.isdigit()):
            return Response({"error": "Phone number must be exactly 10 digits"},status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ====================================== DELETE (SOFT DELETE) ======================================= #
    def delete(self, request, id):
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "You are logged out. Please login first"},status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = User.objects.get(id=id, deleted_at__isnull=True)
        except User.DoesNotExist:
            return Response({"error": "User not found to delete"}, status=status.HTTP_404_NOT_FOUND)

        user.deleted_at = timezone.now()
        user.deleted_by = request.user
        user.save(update_fields=["deleted_at", "deleted_by"])
        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
