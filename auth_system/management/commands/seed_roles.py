from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import Role

class Command(BaseCommand):
    help = "Seed roles into auth_system_role table"

    def handle(self, *args, **kwargs):

        roles = [
            {
                "name": "Admin",
                "code": "ADM",
                "is_default": False
            },
            {
                "name": "Driver",
                "code": "DRI",
                "is_default": False
            },
            {
                "name": "Owner",
                "code": "OWN",
                "is_default": False
            },
            {
                "name": "Customer",
                "code": "CUS",
                "is_default": True   
            },
        ]

        for role_data in roles:
            role, created = Role.objects.get_or_create(
                code=role_data["code"],
                defaults={
                    "name": role_data["name"],
                    "is_default": role_data["is_default"],
                    "is_active": True,
                    "created_at": timezone.now(),
                    "updated_at": timezone.now(),
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created role: {role.name} ({role.code})")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Role already exists: {role.name} ({role.code})")
                )
