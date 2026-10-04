import random
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from kuri.models import KuriScheme, Member, Payment, Notification, AdminProfile


FIRST_NAMES = [
    'Anil', 'Bindu', 'Cyril', 'Divya', 'Elias', 'Fathima', 'Gopan', 'Hema',
    'Irfan', 'Jyothi', 'Kiran', 'Lekha', 'Manoj', 'Nisha', 'Om Prakash',
    'Priya', 'Rajan', 'Sini', 'Thomas', 'Uma',
]
LAST_NAMES = [
    'Nair', 'Menon', 'Varghese', 'Pillai', 'Kutty', 'Raj', 'Thomas',
    'Kumar', 'Jose', 'Krishnan', 'Das', 'Iqbal', 'Mathew', 'Pillai',
    'Nambiar', 'George', 'Devan', 'Suresh', 'Antony', 'Warrier',
]
PLACES = [
    'Kochi', 'Thrissur', 'Kozhikode', 'Kollam', 'Thiruvananthapuram',
    'Alappuzha', 'Palakkad', 'Kannur', 'Malappuram', 'Kottayam',
]
STREETS = ['MG Road', 'Church Street', 'Market Road', 'Beach Road', 'Temple Street', 'Station Road']


class Command(BaseCommand):
    help = 'Seed the database with demo Kuri scheme, 20 fictional members, 40 months of payments and an admin user.'

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)

        self.stdout.write('Clearing old demo data...')
        Payment.objects.all().delete()
        Notification.objects.all().delete()
        Member.objects.all().delete()
        KuriScheme.objects.all().delete()

        self.stdout.write('Creating Kuri scheme...')
        kuri = KuriScheme.objects.create(
            name='KSFE Monthly Kuri - Demo',
            duration_months=40,
            monthly_contribution=2500,
            total_members=20,
            current_month=12,
            status='active',
        )

        self.stdout.write('Creating admin user...')
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True},
        )
        admin_user.email = 'admin@example.com'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password('admin123')
        admin_user.save()

        AdminProfile.objects.update_or_create(
            user=admin_user,
            defaults={
                'name': 'Vishnu K',
                'role': 'Administrator',
                'location': 'Kerala, India',
                'phone': '+91 90000 00000',
            },
        )

        self.stdout.write('Creating 20 fictional members...')
        members = []
        used_names = set()
        for i in range(1, 21):
            while True:
                full_name = f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}'
                if full_name not in used_names:
                    used_names.add(full_name)
                    break
            member_id = f'KM{i:03d}'
            join_offset_days = random.randint(0, 60)
            joining_date = date(2025, 9, 1) - timedelta(days=0) + timedelta(days=join_offset_days - 60)
            dob = date(random.randint(1965, 2000), random.randint(1, 12), random.randint(1, 28))
            is_active = random.random() > 0.1  # ~90% active
            member = Member.objects.create(
                kuri=kuri,
                member_id=member_id,
                name=full_name,
                phone=f'+91 9{random.randint(100000000, 999999999)}',
                email=f'{full_name.lower().replace(" ", ".")}{i}@example.com',
                date_of_birth=dob,
                address=f'{random.randint(1, 200)}, {random.choice(STREETS)}, {random.choice(PLACES)}, Kerala',
                joining_date=joining_date,
                monthly_amount=2500,
                is_active=is_active,
            )
            members.append(member)

        self.stdout.write('Creating 40 months of payment history for each member...')
        today = date.today()
        for member in members:
            for m in range(1, kuri.duration_months + 1):
                due_date = today.replace(day=1) - timedelta(days=30 * (kuri.current_month - m))
                if m > kuri.current_month:
                    status = 'future'
                    paid_date = None
                elif m == kuri.current_month:
                    # current month: mix of paid / pending / overdue
                    status = random.choices(
                        ['paid', 'pending', 'overdue'], weights=[55, 30, 15]
                    )[0]
                    paid_date = due_date if status == 'paid' else None
                else:
                    # past months: mostly paid, some occasional overdue catch-up, rare pending
                    status = random.choices(
                        ['paid', 'overdue', 'pending'], weights=[85, 10, 5]
                    )[0]
                    paid_date = due_date if status == 'paid' else None

                Payment.objects.create(
                    member=member,
                    month_number=m,
                    amount=member.monthly_amount,
                    status=status,
                    due_date=due_date,
                    paid_date=paid_date,
                )

        self.stdout.write('Creating sample notifications...')
        sample_notes = [
            ('Payment reminder', 'Monthly kuri payment for the current month is due soon.', 'reminder'),
            ('Collection completed', 'Month 11 collection has been fully reconciled.', 'payment'),
            ('New member added', 'A new member has joined the kuri scheme.', 'member'),
            ('System update', 'Kuri Management Demo dashboard has been refreshed with new data.', 'system'),
            ('Overdue alert', 'Some members have overdue payments this month. Please follow up.', 'reminder'),
        ]
        for title, msg, ntype in sample_notes:
            Notification.objects.create(title=title, message=msg, notification_type=ntype)

        self.stdout.write(self.style.SUCCESS(
            f'Done! Created 1 kuri scheme, {len(members)} members, '
            f'{Payment.objects.count()} payment records, and the admin user (admin / admin123).'
        ))
