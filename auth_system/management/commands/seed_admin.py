from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decouple import config
from ...models import Role

User = get_user_model()

class Command(BaseCommand):
    help = "Seed Admin user with full profile from .env"

    def handle(self, *args, **kwargs):

        # Get Admin role with code = "ADM"
        try:
            admin_role = Role.objects.get(code="ADM")
        except Role.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("Admin role not found. Please create role with code 'ADM' first.")
            )
            return

        primary_mobile = config("ADMIN_PRIMARY_MOBILE")

        # Check if admin already exists
        if User.objects.filter(primary_mobile_number=primary_mobile).exists():
            self.stdout.write(self.style.WARNING("Admin already exists"))
            return

        # Fetch other values from .env
        secondary_mobile = config("ADMIN_SECONDARY_MOBILE", default=None)
        primary_whatsapp = config("ADMIN_PRIMARY_WHATSAPP", default=primary_mobile)
        secondary_whatsapp = config("ADMIN_SECONDARY_WHATSAPP", default=None)

        admin_email = config("ADMIN_EMAIL")
        admin_password = config("ADMIN_PASSWORD")

        admin = User.objects.create(
            full_name=config("ADMIN_NAME"),

            primary_mobile_number=primary_mobile,
            secondary_mobile_number=secondary_mobile,

            primary_whatsapp_mobile_number=primary_whatsapp,
            secondary_whatsapp_mobile_number=secondary_whatsapp,

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

            latitude=config("ADMIN_LATITUDE", cast=float, default=None),
            longitude=config("ADMIN_LONGITUDE", cast=float, default=None),

            role=admin_role,
            is_active=True,
            is_staff=True,

            created_at=timezone.now(),
        )

        # Set password securely
        admin.set_password(admin_password)
        admin.save()

        # ✅ Terminal output
        self.stdout.write(self.style.SUCCESS("Admin user created successfully"))
        self.stdout.write(self.style.NOTICE(f"Admin Mobile (Primary)   : {primary_mobile}"))
        self.stdout.write(self.style.NOTICE(f"Admin Mobile (Secondary) : {secondary_mobile}"))
        self.stdout.write(self.style.NOTICE(f"Admin Email              : {admin_email}"))
