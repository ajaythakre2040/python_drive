from django.db import models
from django.conf import settings
from django.utils import timezone

class Role(models.Model):
    id = models.BigAutoField(primary_key=True)

    name = models.CharField(max_length=50)
    code = models.CharField(max_length=30, unique=True, default='ROLE_DEFAULT')

    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,blank=True,null=True,related_name='created_roles')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,blank=True,null=True,related_name='updated_roles')
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,blank=True,null=True,related_name='deleted_roles')

    class Meta:
        db_table = 'auth_system_role'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name
        
    def delete(self, *args, **kwargs):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()
        