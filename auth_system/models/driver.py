from django.db import models
from django.conf import settings
from django.utils import timezone
from ..utils.driver_document import driver_document_path

class Driver_Document(models.Model):
    driver = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="driver_documents", null=True, blank=True)

    aadhar_card = models.FileField(upload_to=driver_document_path, blank=True, null=True)
    driving_license = models.FileField(upload_to=driver_document_path, blank=True, null=True)
    pan_card = models.FileField(upload_to=driver_document_path, blank=True, null=True)
    insurance_copy = models.FileField(upload_to=driver_document_path, blank=True, null=True)
    selfie = models.FileField(upload_to=driver_document_path, blank=True, null=True)

    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="created_driver_documents")

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="updated_driver_documents")

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL, related_name="deleted_driver_documents")

    class Meta:
        db_table = "driver_documents"

    def __str__(self):
        return f"Documents - {self.driver.user_id}"

    # ================= SOFT DELETE / RESTORE =================
    def delete(self, user=None):

        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.save()
