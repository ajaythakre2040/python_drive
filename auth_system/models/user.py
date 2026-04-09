from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from ..managers import UserManager, ActiveUserManager
from .Role import Role
from django.db.models import Q

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=20,unique=True,editable=False,null=True,blank=True)

    role = models.ForeignKey(Role,on_delete=models.SET_NULL,null=True,blank=True,related_name="users")

    full_name = models.CharField(max_length=255)

    primary_mobile_number = models.CharField(max_length=10,null=True,blank=True)

    secondary_mobile_number = models.CharField(max_length=10,null=True,blank=True)

    is_primary_whatsapp = models.BooleanField(default=False)

    is_secondary_whatsapp = models.BooleanField(default=False)

    email_id = models.EmailField(blank=True, null=True)

    gender = models.CharField(max_length=10,choices=[("Male", "Male"),("Female", "Female"),("Other", "Other"),])

    dob = models.DateField()

    current_address = models.TextField(blank=True, null=True)

    permanent_address = models.TextField(blank=True, null=True)

    latitude = models.DecimalField(max_digits=10,decimal_places=7,blank=True,null=True)

    longitude = models.DecimalField(max_digits=10,decimal_places=7,blank=True,null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    is_blocked = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="created_users")

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="updated_users")

    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name="deleted_users")

    objects = ActiveUserManager()
    all_objects = UserManager()

    USERNAME_FIELD = "user_id"
    REQUIRED_FIELDS = []

    class Meta:
        constraints = [
            # Primary mobile unique per role
            models.UniqueConstraint(
                fields=['primary_mobile_number', 'role'],
                name='unique_mobile_per_role'
            ),

            # Email unique per role (ignore null)
            models.UniqueConstraint(
                fields=['email_id', 'role'],
                condition=Q(email_id__isnull=False),
                name='unique_email_per_role'
            ),
        ]

    def save(self, *args, **kwargs):
        # Default role assign
        if not self.role:
            self.role = Role.objects.filter(
                is_default=True,
                is_active=True
            ).first()

        # Admin → staff
        if self.role and self.role.code == "ADMIN":
            self.is_staff = True

        # 🔥 Secondary Mobile Safety (MODEL LEVEL CHECK)
        if self.secondary_mobile_number:
            if self.secondary_mobile_number == self.primary_mobile_number:
                raise ValueError("Primary and Secondary mobile cannot be same")

            # Secondary number kisi aur ka primary na ho
            from auth_system.models import User
            if User.all_objects.filter(
                primary_mobile_number=self.secondary_mobile_number
            ).exclude(id=self.id).exists():
                raise ValueError("Secondary number already used as primary")

        super().save(*args, **kwargs)

    def delete(self, user=None):
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()

    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.save()

    def __str__(self):
        return (
            f"{self.user_id or 'NO_ID'} | "
            f"{self.primary_mobile_number} | "
            f"{self.role.code if self.role else 'NO_ROLE'}"
        )