from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decouple import config
from ...models import Role

User = get_user_model()


class Command(BaseCommand):
    help = "Seed Admin user (WhatsApp boolean only)"

    def handle(self, *args, **kwargs):

        # Get Admin role
        try:
            admin_role = Role.objects.get(code="ADM")
        except Role.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "Admin role not found. Please create role with code 'ADM' first."
                )
            )
            return

        # -------- Mobile Numbers --------
        primary_mobile_number = config("ADMIN_PRIMARY_MOBILE_NUMBER")

        if User.objects.filter(primary_mobile_number=primary_mobile_number).exists():
            self.stdout.write(self.style.WARNING("Admin already exists"))
            return

        secondary_mobile_number = config(
            "ADMIN_SECONDARY_MOBILE_NUMBER", default=None
        )

        # -------- WhatsApp BOOLEAN ONLY --------
        is_primary_whatsapp = config(
            "ADMIN_IS_PRIMARY_WHATSAPP", cast=bool, default=True
        )
        is_secondary_whatsapp = config(
            "ADMIN_IS_SECONDARY_WHATSAPP", cast=bool, default=False
        )

        # -------- Other details --------
        admin_email = config("ADMIN_EMAIL")
        admin_password = config("ADMIN_PASSWORD")

        latitude_val = config("ADMIN_LATITUDE", default=None)
        longitude_val = config("ADMIN_LONGITUDE", default=None)

        admin = User.objects.create(
            full_name=config("ADMIN_NAME"),

            primary_mobile_number=primary_mobile_number,
            secondary_mobile_number=secondary_mobile_number,

            # ✅ WhatsApp flags
            is_primary_whatsapp=is_primary_whatsapp,
            is_secondary_whatsapp=is_secondary_whatsapp,

            email_id=admin_email,
            gender=config("ADMIN_GENDER"),
            dob=config("ADMIN_DOB"),

            current_address=config(
                "ADMIN_CURRENT_ADDRESS", default="Head Office"
            ),
            permanent_address=config(
                "ADMIN_PERMANENT_ADDRESS", default="Permanent Address"
            ),

            latitude=float(latitude_val) if latitude_val else None,
            longitude=float(longitude_val) if longitude_val else None,

            role=admin_role,
            is_active=True,
            is_staff=True,
            created_at=timezone.now(),
        )

        admin.set_password(admin_password)
        admin.save()

        # -------- Output --------
        self.stdout.write(self.style.SUCCESS("Admin user created successfully"))
        self.stdout.write(
            self.style.NOTICE(f"Primary Mobile Number : {primary_mobile_number}")
        )
        self.stdout.write(
            self.style.NOTICE(f"Admin Email          : {admin_email}")
        )
        self.stdout.write(
            self.style.NOTICE(f"Admin Password       : {admin_password}")
        )
