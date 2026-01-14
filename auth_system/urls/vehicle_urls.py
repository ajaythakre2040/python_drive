from django.urls import path
from ..views.vehicles_views import VehicleAPIView

urlpatterns = [
    path("vehicles/", VehicleAPIView.as_view()),
    path("vehicles/<int:id>/", VehicleAPIView.as_view()),
]
