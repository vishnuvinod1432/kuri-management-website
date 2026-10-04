from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.utils import timezone


AVATAR_COLORS = [
    '#6C5CE7', '#00B894', '#0984E3', '#E17055', '#FDCB6E',
    '#D63031', '#00CEC9', '#E84393', '#636E72', '#2D3436',
]


class KuriScheme(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('paused', 'Paused'),
    ]

    name = models.CharField(max_length=200, default='KSFE Monthly Kuri - Demo')
    duration_months = models.PositiveIntegerField(default=40)
    monthly_contribution = models.DecimalField(max_digits=10, decimal_places=2, default=2500)
    total_members = models.PositiveIntegerField(default=20)
    current_month = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kuri Scheme'
        verbose_name_plural = 'Kuri Schemes'

    def __str__(self):
        return self.name

    @property
    def expected_monthly_collection(self):
        return self.monthly_contribution * self.total_members

    @property
    def remaining_months(self):
        return max(self.duration_months - self.current_month, 0)


class Member(models.Model):
    kuri = models.ForeignKey(KuriScheme, on_delete=models.CASCADE, related_name='members')
    member_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    joining_date = models.DateField(default=timezone.now)
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, default=2500)
    is_active = models.BooleanField(default=True)
    avatar_color = models.CharField(max_length=10, default='#6C5CE7')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['member_id']

    def __str__(self):
        return f'{self.member_id} - {self.name}'

    def save(self, *args, **kwargs):
        if not self.avatar_color or self.avatar_color == '#6C5CE7':
            idx = sum(ord(c) for c in (self.member_id or self.name or 'X')) % len(AVATAR_COLORS)
            self.avatar_color = AVATAR_COLORS[idx]
        super().save(*args, **kwargs)

    @property
    def initials(self):
        parts = self.name.split()
        letters = ''.join(p[0] for p in parts[:2]).upper()
        return letters or 'M'

    @property
    def total_paid(self):
        agg = self.payments.filter(status='paid').aggregate(total=Sum('amount'))
        return agg['total'] or 0

    @property
    def total_pending(self):
        agg = self.payments.filter(status__in=['pending', 'overdue']).aggregate(total=Sum('amount'))
        return agg['total'] or 0

    @property
    def months_paid(self):
        return self.payments.filter(status='paid').count()

    @property
    def months_pending(self):
        return self.payments.filter(status__in=['pending', 'overdue']).count()

    @property
    def months_overdue(self):
        return self.payments.filter(status='overdue').count()

    @property
    def payment_progress_percent(self):
        total = self.kuri.duration_months or 1
        return round((self.months_paid / total) * 100, 1)

    @property
    def current_status_label(self):
        current = self.payments.filter(month_number=self.kuri.current_month).first()
        if current:
            return current.get_status_display()
        return 'Unknown'


class Payment(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
        ('future', 'Future'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    month_number = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=2500)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='future')
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['month_number']
        unique_together = ('member', 'month_number')

    def __str__(self):
        return f'{self.member.member_id} - Month {self.month_number} - {self.status}'

    def save(self, *args, **kwargs):
        if self.status == 'paid' and not self.paid_date:
            self.paid_date = timezone.now().date()
        if self.status != 'paid':
            self.paid_date = None
        super().save(*args, **kwargs)


class Notification(models.Model):
    TYPE_CHOICES = [
        ('payment', 'Payment'),
        ('reminder', 'Reminder'),
        ('system', 'System'),
        ('member', 'Member'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    name = models.CharField(max_length=150, default='Vishnu K')
    role = models.CharField(max_length=100, default='Administrator')
    location = models.CharField(max_length=150, default='Kerala, India')
    phone = models.CharField(max_length=20, default='+91 90000 00000')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'

    def __str__(self):
        return self.name
