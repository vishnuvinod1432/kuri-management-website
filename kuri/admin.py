from django.contrib import admin
from .models import KuriScheme, Member, Payment, Notification, AdminProfile


@admin.register(KuriScheme)
class KuriSchemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_months', 'monthly_contribution', 'total_members', 'current_month', 'status')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'name', 'phone', 'is_active', 'joining_date', 'monthly_amount')
    search_fields = ('member_id', 'name', 'phone', 'email')
    list_filter = ('is_active',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('member', 'month_number', 'amount', 'status', 'due_date', 'paid_date')
    list_filter = ('status', 'month_number')
    search_fields = ('member__name', 'member__member_id')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'location', 'phone')
