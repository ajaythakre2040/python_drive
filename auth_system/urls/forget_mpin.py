from django.urls import path
from ..views.forget_mpin import ForgetMPINAPIView

urlpatterns = [
    path("forget-mpin/", ForgetMPINAPIView.as_view(), name="forget-mpin"),
]