from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from ..permission.authentication import LoginTokenAuthentication
from ..models.driver import Driver_Document
from ..serializer.driver import DriverDocumentSerializer

User = get_user_model()

class DriverDocumentAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]

    FILE_FIELDS = ["aadhar_card","driving_license","pan_card","insurance_copy","selfie",]

    # ================= GET =================
    def get(self, request, user_id):
        try:
            user = User.all_objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"status": False, "message": "Invalid user_id"},status=status.HTTP_404_NOT_FOUND,)

        document = Driver_Document.objects.filter(driver=user, deleted_at__isnull=True).first()

        if not document:
            return Response({"status": False, "message": "Driver document not found"},status=status.HTTP_404_NOT_FOUND,)

        serializer = DriverDocumentSerializer(document)
        return Response({"status": True, "data": serializer.data},status=status.HTTP_200_OK,)

    # ================= POST (CREATE / UPDATE) =================
    def post(self, request, user_id):
        try:
            user = User.all_objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"status": False, "message": "Invalid user_id"},status=status.HTTP_404_NOT_FOUND,)

        defaults = {"created_by": request.user,"updated_by": request.user,}

        for field in self.FILE_FIELDS:
            if field in request.FILES:
                defaults[field] = request.FILES.get(field)

        document, created = Driver_Document.objects.update_or_create(driver=user,defaults=defaults,)

        serializer = DriverDocumentSerializer(document)
        return Response({"status": True, "data": serializer.data},status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,)

    # ================= PATCH =================
    def patch(self, request, user_id):
        try:
            user = User.all_objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"status": False, "message": "Invalid user_id"},status=status.HTTP_404_NOT_FOUND,)

        document = Driver_Document.objects.filter(driver=user, deleted_at__isnull=True).first()

        if not document:
            return Response({"status": False, "message": "Driver document not found"},status=status.HTTP_404_NOT_FOUND,)

        data = request.data.copy()

        for field in self.FILE_FIELDS:
            if field in request.FILES:
                data[field] = request.FILES.get(field)

        serializer = DriverDocumentSerializer(document, data=data, partial=True)

        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response({"status": True, "data": serializer.data},status=status.HTTP_200_OK,)

        return Response({"status": False, "errors": serializer.errors},status=status.HTTP_400_BAD_REQUEST,)

    # ================= DELETE (SOFT DELETE) =================
    def delete(self, request, user_id):
        try:
            user = User.all_objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({"status": False, "message": "Invalid user_id"},status=status.HTTP_404_NOT_FOUND,)

        document = Driver_Document.objects.filter(driver=user, deleted_at__isnull=True).first()

        if not document:
            return Response({"status": False, "message": "Driver document not found"},status=status.HTTP_404_NOT_FOUND,)

        document.deleted_at = timezone.now()
        document.deleted_by = request.user
        document.save(update_fields=["deleted_at", "deleted_by"])

        return Response({"status": True, "message": "Driver document deleted successfully"},status=status.HTTP_200_OK,)
