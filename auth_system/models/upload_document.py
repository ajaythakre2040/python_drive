from django.db import models
from django.conf import settings
import uuid, os

def user_document_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    random_name = uuid.uuid4().hex
    return f"{instance.user.role}/{instance.user.user_id}/{random_name}{ext}"

class User_Documents(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="documents")

    aadhaar_card = models.FileField(upload_to=user_document_path, blank=True, null=True)
    driving_license = models.FileField(upload_to=user_document_path, blank=True, null=True)
    pan_card = models.FileField(upload_to=user_document_path, blank=True, null=True)
    rc = models.FileField(upload_to=user_document_path, blank=True, null=True)
    insurance_copy = models.FileField(upload_to=user_document_path, blank=True, null=True)
    selfie = models.FileField(upload_to=user_document_path, blank=True, null=True)

    is_aadhaar_verified = models.BooleanField(default=False)
    is_dl_verified = models.BooleanField(default=False)
    is_pan_verified = models.BooleanField(default=False)
    is_rc_verified = models.BooleanField(default=False)
    is_insurance_verified = models.BooleanField(default=False)
    is_selfie_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True,on_delete=models.SET_NULL,related_name="created_documents")

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True,on_delete=models.SET_NULL,related_name="updated_documents")

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True,on_delete=models.SET_NULL,related_name="deleted_documents")

    def __str__(self):
        return f"Documents - {self.user.user_id}"
