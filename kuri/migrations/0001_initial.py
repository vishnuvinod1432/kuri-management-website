import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='KuriScheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='KSFE Monthly Kuri - Demo', max_length=200)),
                ('duration_months', models.PositiveIntegerField(default=40)),
                ('monthly_contribution', models.DecimalField(decimal_places=2, default=2500, max_digits=10)),
                ('total_members', models.PositiveIntegerField(default=20)),
                ('current_month', models.PositiveIntegerField(default=1)),
                ('status', models.CharField(choices=[('active', 'Active'), ('closed', 'Closed'), ('paused', 'Paused')], default='active', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Kuri Scheme',
                'verbose_name_plural': 'Kuri Schemes',
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_id', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=150)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('address', models.TextField(blank=True)),
                ('joining_date', models.DateField(default=django.utils.timezone.now)),
                ('monthly_amount', models.DecimalField(decimal_places=2, default=2500, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('avatar_color', models.CharField(default='#6C5CE7', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('kuri', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='kuri.kurischeme')),
            ],
            options={
                'ordering': ['member_id'],
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month_number', models.PositiveIntegerField()),
                ('amount', models.DecimalField(decimal_places=2, default=2500, max_digits=10)),
                ('status', models.CharField(choices=[('paid', 'Paid'), ('pending', 'Pending'), ('overdue', 'Overdue'), ('future', 'Future')], default='future', max_length=10)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('paid_date', models.DateField(blank=True, null=True)),
                ('notes', models.CharField(blank=True, max_length=255)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='kuri.member')),
            ],
            options={
                'ordering': ['month_number'],
                'unique_together': {('member', 'month_number')},
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('notification_type', models.CharField(choices=[('payment', 'Payment'), ('reminder', 'Reminder'), ('system', 'System'), ('member', 'Member')], default='system', max_length=20)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('member', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='kuri.member')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='AdminProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Vishnu K', max_length=150)),
                ('role', models.CharField(default='Administrator', max_length=100)),
                ('location', models.CharField(default='Kerala, India', max_length=150)),
                ('phone', models.CharField(default='+91 90000 00000', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='admin_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Admin Profile',
                'verbose_name_plural': 'Admin Profiles',
            },
        ),
    ]
