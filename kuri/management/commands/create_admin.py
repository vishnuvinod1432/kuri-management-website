import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create admin user if it does not exist"

    def handle(self, *args, **kwargs):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not password:
            self.stdout.write("Admin password is not configured.")
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"User '{username}' already exists.")
            return

        User.objects.create_superuser(
            username=username,
            email="admin@example.com",
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Admin user '{username}' created successfully."
            )
        )