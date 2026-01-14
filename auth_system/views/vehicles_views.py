from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models.vehicle import Vehicle
from django.utils import timezone
from ..utils.sanitize import no_html_validator
from ..serializer.vehicles import VehicleSerializer
from ..utils.pagination import CustomPagination
from ..permission.authentication import LoginTokenAuthentication
from rest_framework.permissions import IsAuthenticated

SANITIZE_FIELDS=["rc_number"]

class VehicleAPIView(APIView):
    authentication_classes = [LoginTokenAuthentication]
    permission_classes = [IsAuthenticated]
#============================================GET/GET BY ID=====================================#
    def get(self,request,id=None):
        if not request.user or not request.user.is_authenticated:
            return Response({"error":"you are logged out Please login first"},status = status.HTTP_401_UNAUTHORIZED)
        
        try:
            if id:
                vehicle = vehicle.objects.get(id=id,deleted_at__isnull =True)
                serializer= VehicleSerializer(vehicle)
                return Response(serializer.data,status=status.HTTP_200_OK)
            
            vehicles = vehicle.objects.filter(deleted_at__isnull = True)
            paginator =CustomPagination()
            paginated_queryset =paginator.paginate_queryset(vehicles,request, view=self)

            serializer = VehicleSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        except vehicle.DoesNotExist():
            return Response({"error":"Vehicle not found"},status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": f"Something went wrong:{str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#========================================POST=========================================#
    def post(self,request):
        if not request.user or not request.user.is_authenticated:
            return Response({"error":"You are logged out please login first"},status=status.HTTP_401_UNAUTHORIZED)
        
        data=request.data.copy()
        for field in SANITIZE_FIELDS:
            if  field in data and data[field]:
                try:
                    data[field] = no_html_validator(data[field])
                
                except Exception as e:
                    return Response({"error":f"Invalid input in {field}:{str(e)}"},status=status.HTTP_400_BAD_REQUEST)
        
        serializer = VehicleSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save(owner = request.user,created_by = request.user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#================================PATCH========================================#
    def patch(self, request, id):
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "You are logged out. Please login first"},status=status.HTTP_401_UNAUTHORIZED)

        try:
            vehicle = Vehicle.objects.get(id=id,deleted_at__isnull=True)
        
        except Vehicle.DoesNotExist:
            return Response({"error": "Vehicle not found to update"},status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()

        for field in SANITIZE_FIELDS:
            if field in data and data[field]:
                try:
                    data[field] = no_html_validator(data[field])
                except Exception as e:
                    return Response({"error": f"Invalid input in {field}: {str(e)}"},status=status.HTTP_400_BAD_REQUEST)

        serializer = VehicleSerializer(vehicle,data=data,partial=True)

        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data,status=status.HTTP_200_OK)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#==========================================DELETE=================================================#

    def delete(self, request, id):
        if not request.user or not request.user.is_authenticated:
            return Response({"error": "You are logged out. Please login first"},status=status.HTTP_401_UNAUTHORIZED)

        try:
            vehicle = Vehicle.objects.get(id=id,deleted_at__isnull=True)
        
        except Vehicle.DoesNotExist:
            return Response({"error": "Vehicle not found to delete"},status=status.HTTP_404_NOT_FOUND)

        vehicle.deleted_at = timezone.now()
        vehicle.deleted_by = request.user
        vehicle.save(update_fields=["deleted_at", "deleted_by"])

        return Response({"message": "Vehicle deleted successfully"},status=status.HTTP_200_OK)
    
