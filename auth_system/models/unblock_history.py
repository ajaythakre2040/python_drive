from django.db import models
from django.conf import settings

class UserBlockHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="block_histories")

    email_id = models.EmailField(blank=True, null=True)
    primary_mobile_number = models.CharField(max_length=10, blank=True, null=True)

    is_unblocked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="created_user_blocks")

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="updated_user_blocks")

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="deleted_user_blocks")

    class Meta:
        db_table = "user_block_history"
        ordering = ["-created_at"]

    def __str__(self):
        return  str(self.user)