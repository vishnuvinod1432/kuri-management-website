from django.db import migrations
import os


def create_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')

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
        user.save()
    else:
        User.objects.create_superuser(
            username=username,
            email='admin@example.com',
            password=password
        )


class Migration(migrations.Migration):

    dependencies = [
        ('kuri', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]