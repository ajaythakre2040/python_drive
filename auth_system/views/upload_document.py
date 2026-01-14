from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from ..permission.authentication import LoginTokenAuthentication
from ..models import User, User_Documents
from ..serializer import DocumentUploadSerializer
from ..utils.pagination import CustomPagination
from ..utils.sanitize import no_html_validator

class UserDocumentsAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    # ================= GET ================= #
    def get(self, request, user_id=None):
        if user_id:
            try:
                user = User.objects.get(user_id=user_id)
                documents = User_Documents.objects.filter(user=user, deleted_at__isnull=True).first()
                if not documents:
                    return Response({"error": "Documents not found"}, status=status.HTTP_404_NOT_FOUND)
                serializer = DocumentUploadSerializer(documents)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "Invalid user_id"}, status=status.HTTP_404_NOT_FOUND)

        queryset = User_Documents.objects.filter(deleted_at__isnull=True)
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=self)
        serializer = DocumentUploadSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    # ================= POST (UPLOAD) ================= #
    def post(self, request):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid user_id"}, status=status.HTTP_404_NOT_FOUND)

        documents, _ = User_Documents.objects.get_or_create(user=user)
        serializer = DocumentUploadSerializer(documents, data=request.data, partial=True)

        if serializer.is_valid():
            for field in ["aadhaar_card", "driving_license", "pan_card", "rc", "insurance_copy", "selfie"]:
                file_obj = serializer.validated_data.get(field)
                if file_obj and hasattr(file_obj, "name"):
                    try:
                        file_obj.name = no_html_validator(file_obj.name)
                    except Exception as e:
                        return Response({"status": False, "message": str(e)}, status=400)

            serializer.save(user=user)
            return Response(
                {
                    "message": "Documents uploaded successfully",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ================= PATCH (UPDATE) ================= #
    def patch(self, request, user_id=None):
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user_id=user_id)
            documents = User_Documents.objects.get(user=user, deleted_at__isnull=True)
        except User.DoesNotExist:
            return Response({"error": "Invalid user_id"}, status=status.HTTP_404_NOT_FOUND)
        except User_Documents.DoesNotExist:
            return Response({"error": "Documents not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentUploadSerializer(documents, data=request.data, partial=True)

        if serializer.is_valid():
            for field in ["aadhaar_card", "driving_license", "pan_card", "rc", "insurance_copy", "selfie"]:
                file_obj = serializer.validated_data.get(field)
                if file_obj and hasattr(file_obj, "name"):
                    try:
                        file_obj.name = no_html_validator(file_obj.name)
                    except Exception as e:
                        return Response({"status": False, "message": str(e)}, status=400)

            serializer.save()
            return Response(
                {
                    "message": "Documents updated successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ================= DELETE (SOFT DELETE) ================= #
    def delete(self, request, user_id=None):
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(user_id=user_id)
            documents = User_Documents.objects.get(user=user, deleted_at__isnull=True)
        except User.DoesNotExist:
            return Response({"error": "Invalid user_id"}, status=status.HTTP_404_NOT_FOUND)
        except User_Documents.DoesNotExist:
            return Response({"error": "Documents not found"}, status=status.HTTP_404_NOT_FOUND)

        documents.deleted_at = timezone.now()
        documents.deleted_by = request.user
        documents.save(update_fields=["deleted_at", "deleted_by"])

        return Response({"message": "Documents deleted successfully"}, status=status.HTTP_200_OK)
