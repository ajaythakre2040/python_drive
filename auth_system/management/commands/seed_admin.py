from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decouple import config
from ...models import Role

User = get_user_model()

class Command(BaseCommand):
    help = "Seed Admin user with full profile from .env"

    def handle(self, *args, **kwargs):

        try:
            admin_role = Role.objects.get(code="ADM")
        except Role.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("Admin role not found. Please run seed_roles first.")
            )
            return

        mobile = config("ADMIN_MOBILE")

        if User.objects.filter(primary_mobile_number=mobile).exists():
            self.stdout.write(self.style.WARNING("Admin already exists"))
            return

        admin_email = config("ADMIN_EMAIL")
        admin_password = config("ADMIN_PASSWORD")

        admin = User.objects.create(
            full_name=config("ADMIN_NAME"),
            primary_mobile_number=mobile,
            secondary_mobile_number=False,

            primary_whatsapp_mobile_number=config(
                "ADMIN_WHATSAPP", default=mobile
            ),
            secondary_whatsapp_mobile_number=False,

            email_id=admin_email,
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

        admin.set_password(admin_password)
        admin.save()

        # ✅ TERMINAL OUTPUT
        self.stdout.write(self.style.SUCCESS("Admin user created successfully"))
        self.stdout.write(self.style.NOTICE(f"Admin Email    : {admin_email}"))
        self.stdout.write(self.style.NOTICE(f"Admin Password : {admin_password}"))
