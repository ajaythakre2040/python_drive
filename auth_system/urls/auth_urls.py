from django.urls import path
from auth_system.views.auth_views import (RegisterAPIView, LoginAPIView,LogoutAPIView, ChangePasswordAPIView,ResetPasswordAPIView)

urlpatterns = [
    path('<str:role_name>/register/', RegisterAPIView.as_view(), name='role-register'),
    path('<str:role_name>/login/', LoginAPIView.as_view(), name='role-login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
]
