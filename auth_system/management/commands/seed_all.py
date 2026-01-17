from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Run all seeders (roles, admin, etc.)"

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.NOTICE("Running role seeder..."))
        call_command("seed_roles")

        self.stdout.write(self.style.NOTICE("Running admin seeder..."))
        call_command("seed_admin")

        self.stdout.write(self.style.SUCCESS("All seeders executed successfully"))
