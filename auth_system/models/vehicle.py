from django.db import models
from django.conf import settings
from django.utils import timezone


class Vehicle(models.Model):

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="vehicles")

    rc_number = models.CharField(max_length=20,unique=True)

    # ================= AUDIT FIELDS =================
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="created_vehicles")

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="updated_vehicles")

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="deleted_vehicles")

    class Meta:
        db_table = "vehicles"

    def __str__(self):
        return f"{self.rc_number} - Owner:{self.owner.user_id}"

    # ================= SOFT DELETE =================
    def delete(self, user=None):
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.save()
