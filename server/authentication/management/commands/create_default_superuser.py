from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Create a superuser with default credentials if it does not exist'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin'
        
        try:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Superuser "{username}" created successfully with password "{password}"'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Superuser "{username}" already exists'
                    )
                )
        except IntegrityError as e:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Superuser "{username}" already exists (IntegrityError caught: {str(e)})'
                )
            )
