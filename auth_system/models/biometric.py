from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

class User_security(models.Model):
    user= models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    # ===== MPIN =====
    mpin_hash = models.CharField(max_length=128, blank=True, null=True)
    is_mpin_enabled = models.BooleanField(default=True)
    
    is_fingerprint_enabled = models.BooleanField(default=True)

    is_face_lock_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL, related_name='created_usersecurities')

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL, related_name='updated_usersecurities')

    deleted_at = models.DateTimeField(null=True,blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL, related_name='deleted_usersecurities')
    
    def __str__(self):
        return f"Security - {self.user.user_id}"

    # ===== MPIN helpers =====
    def set_mpin(self, raw_mpin):
        """MPIN set and hashed"""
        self.mpin_hash = make_password(raw_mpin)
        self.save()

    def check_mpin(self, raw_mpin):
        """Check MPIN against stored hash"""
        if not self.mpin_hash:
            return False
        return check_password(raw_mpin, self.mpin_hash)