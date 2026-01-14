from django.urls import path
from ..views.biometric import UserSecurityAPIView

urlpatterns = [
    path('usersecurity/',UserSecurityAPIView.as_view()),
    path('usersecurity/<str:user_id>/',UserSecurityAPIView.as_view()),
]

