from django.urls import path
from ..views.driver_views import DriverDocumentAPIView

urlpatterns = [
    path("driver-documents/<str:user_id>/", DriverDocumentAPIView.as_view()),
]