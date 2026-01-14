from django.urls import path
from ..views.user_views import UserAPIView

urlpatterns = [
    path("User/", UserAPIView.as_view(),name="User-list"),
    path("User/<int:id>/",UserAPIView.as_view(),name="User-details"),
]