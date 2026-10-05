import os

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class KuriConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kuri'
    verbose_name = 'Kuri Management Demo'

    def ready(self):

        from django.contrib.auth import get_user_model

        def create_or_update_admin(sender, **kwargs):

            User = get_user_model()

            username = os.environ.get(
                'DJANGO_SUPERUSER_USERNAME',
                'admin'
            )

            password = os.environ.get(
                'DJANGO_SUPERUSER_PASSWORD'
            )

            if not password:
                return

            user = User.objects.filter(username=username).first()

            if user:
                user.set_password(password)
                user.is_staff = True
                user.is_superuser = True
                user.save(
                    update_fields=[
                        'password',
                        'is_staff',
                        'is_superuser'
                    ]
                )
            else:
                User.objects.create_superuser(
                    username=username,
                    email='admin@example.com',
                    password=password
                )

        post_migrate.connect(
            create_or_update_admin,
            sender=self,
            dispatch_uid='kuri.create_or_update_admin'
        )