from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decouple import config
from ...models import Role

User = get_user_model()


class Command(BaseCommand):
    help = "Seed Admin user with full profile from .env"

    def handle(self, *args, **kwargs):

        admin_role, _ = Role.objects.get_or_create(
            code="ADMIN",
            defaults={
                "name": "Admin",
                "is_active": True,
                "is_default": False
            }
        )

        mobile = config("ADMIN_MOBILE")

        if User.objects.filter(primary_mobile_number=mobile).exists():
            self.stdout.write(self.style.WARNING("Admin already exists"))
            return

        admin = User.objects.create(
            full_name=config("ADMIN_NAME"),
            primary_mobile_number=mobile,
            secondary_mobile_number=False,

            primary_whatsapp_mobile_number=config(
                "ADMIN_WHATSAPP", default=mobile
            ),
            secondary_whatsapp_mobile_number=False,

            email_id=config("ADMIN_EMAIL"),
            gender=config("ADMIN_GENDER"),
            dob=config("ADMIN_DOB"),

            current_address=config(
                "ADMIN_CURRENT_ADDRESS",
                default="Head Office Address"
            ),
            permanent_address=config(
                "ADMIN_PERMANENT_ADDRESS",
                default="Permanent Address"
            ),

            latitude=config("ADMIN_LATITUDE", default=None),
            longitude=config("ADMIN_LONGITUDE", default=None),

            role=admin_role,
            is_active=True,
            is_staff=True,

            created_at=timezone.now(),
        )

        admin.set_password(config("ADMIN_PASSWORD"))
        admin.save()

        self.stdout.write(self.style.SUCCESS("Admin user with address created successfully"))
