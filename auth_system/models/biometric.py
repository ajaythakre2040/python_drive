from django.db import models
from django.conf import settings
from ..utils.mpin_crypto import encrypt_mpin, decrypt_mpin

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
    def set_mpin(self, raw_mpin):
        self.mpin_hash = encrypt_mpin(raw_mpin)
        self.save()

    def check_mpin(self, raw_mpin):
        if not self.mpin_hash:
            return False
        return decrypt_mpin(self.mpin_hash) == raw_mpin

    def get_mpin(self):
        if not self.mpin_hash:
            return None
        return decrypt_mpin(self.mpin_hash)