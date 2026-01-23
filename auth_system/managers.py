from django.db import models
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):

    def create_user(self, primary_mobile_number, password=None, **extra_fields):
        if not primary_mobile_number:
            raise ValueError("Primary mobile number is required")

        user = self.model(primary_mobile_number=primary_mobile_number,**extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, primary_mobile_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(primary_mobile_number, password, **extra_fields)

class ActiveUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            deleted_at__isnull=True
        )