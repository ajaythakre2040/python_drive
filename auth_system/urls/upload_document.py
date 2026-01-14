from django.urls import path 
from ..views.upload_document import UserDocumentsAPIView

urlpatterns = [
    path('userdocuments/',UserDocumentsAPIView.as_view()),
    path('userdocuments/<str:user_id>/',UserDocumentsAPIView.as_view()),
]
