from django.conf import settings
from django.db import models

class UserMPINHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="mpin_histories")
    mpin = models.CharField(max_length=128) 

    mpin_attempts = models.IntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="mpin_history_created_by")

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="mpin_history_updated_by")

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name="mpin_history_deleted_by")

    class Meta:
        db_table = "user_mpin_history"
        ordering = ["-created_at"]

    def __str__(self):
        return f"MPIN History - {self.user_id}"