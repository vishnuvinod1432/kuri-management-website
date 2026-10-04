import json
from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import KuriScheme, Member, Payment, Notification, AdminProfile
from .forms import MemberForm, PaymentEditForm, AdminProfileForm


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid username or password. Try admin / admin123.')

    return render(request, 'kuri/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    kuri = KuriScheme.objects.first()
    members = Member.objects.filter(kuri=kuri) if kuri else Member.objects.none()

    total_members = members.count()
    active_members = members.filter(is_active=True).count()
    inactive_members = members.filter(is_active=False).count()

    current_month = kuri.current_month if kuri else 1

    paid_this_month = Payment.objects.filter(
        member__kuri=kuri, month_number=current_month, status='paid'
    ).count()
    pending_this_month = Payment.objects.filter(
        member__kuri=kuri, month_number=current_month, status__in=['pending', 'overdue']
    ).count()

    total_collected = Payment.objects.filter(member__kuri=kuri, status='paid').aggregate(
        total=Sum('amount'))['total'] or 0
    total_pending = Payment.objects.filter(
        member__kuri=kuri, status__in=['pending', 'overdue']).aggregate(
        total=Sum('amount'))['total'] or 0

    # Chart data: collected amount per month (1..current_month)
    chart_labels = []
    chart_values = []
    max_month = current_month if kuri else 0
    for m in range(1, max_month + 1):
        total = Payment.objects.filter(
            member__kuri=kuri, month_number=m, status='paid').aggregate(
            total=Sum('amount'))['total'] or 0
        chart_labels.append(f'M{m}')
        chart_values.append(float(total))

    recent_notifications = Notification.objects.all()[:5]

    context = {
        'kuri': kuri,
        'total_members': total_members,
        'active_members': active_members,
        'inactive_members': inactive_members,
        'paid_this_month': paid_this_month,
        'pending_this_month': pending_this_month,
        'total_collected': total_collected,
        'total_pending': total_pending,
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
        'recent_notifications': recent_notifications,
        'active_page': 'dashboard',
    }
    return render(request, 'kuri/dashboard.html', context)


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

@login_required
def members_list(request):
    kuri = KuriScheme.objects.first()
    members = Member.objects.filter(kuri=kuri) if kuri else Member.objects.none()

    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', 'member_id')

    if query:
        members = members.filter(
            Q(name__icontains=query) | Q(member_id__icontains=query) |
            Q(phone__icontains=query) | Q(email__icontains=query)
        )

    if status_filter == 'active':
        members = members.filter(is_active=True)
    elif status_filter == 'inactive':
        members = members.filter(is_active=False)

    valid_sorts = ['member_id', 'name', 'joining_date', '-joining_date']
    if sort_by in valid_sorts:
        members = members.order_by(sort_by)

    context = {
        'kuri': kuri,
        'members': members,
        'query': query,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'active_page': 'members',
    }
    return render(request, 'kuri/members.html', context)


@login_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    payments = member.payments.all().order_by('month_number')
    context = {
        'member': member,
        'payments': payments,
        'active_page': 'members',
    }
    return render(request, 'kuri/member_detail.html', context)


@login_required
def member_add(request):
    kuri = KuriScheme.objects.first()
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.kuri = kuri
            member.save()
            # Create payment rows for all months of the scheme
            for m in range(1, kuri.duration_months + 1):
                if m < kuri.current_month:
                    status = 'paid'
                elif m == kuri.current_month:
                    status = 'pending'
                else:
                    status = 'future'
                Payment.objects.create(
                    member=member, month_number=m,
                    amount=member.monthly_amount, status=status,
                )
            Notification.objects.create(
                title='New member added',
                message=f'{member.name} ({member.member_id}) joined the kuri.',
                notification_type='member', member=member,
            )
            messages.success(request, f'Member {member.name} added successfully.')
            return redirect('members')
    else:
        form = MemberForm()
    return render(request, 'kuri/member_form.html', {'form': form, 'mode': 'add', 'active_page': 'members'})


@login_required
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f'Member {member.name} updated successfully.')
            return redirect('member_detail', pk=member.pk)
    else:
        form = MemberForm(instance=member)
    return render(request, 'kuri/member_form.html', {'form': form, 'mode': 'edit', 'member': member, 'active_page': 'members'})


@login_required
@require_POST
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    name = member.name
    member.delete()
    messages.success(request, f'Member {name} deleted.')
    return redirect('members')


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

@login_required
def payments_list(request):
    kuri = KuriScheme.objects.first()
    month = int(request.GET.get('month', kuri.current_month if kuri else 1))
    status_filter = request.GET.get('status', '')

    payments = Payment.objects.filter(member__kuri=kuri, month_number=month).select_related('member')
    if status_filter:
        payments = payments.filter(status=status_filter)

    context = {
        'kuri': kuri,
        'payments': payments.order_by('member__member_id'),
        'month': month,
        'status_filter': status_filter,
        'month_range': range(1, (kuri.duration_months if kuri else 40) + 1),
        'active_page': 'payments',
    }
    return render(request, 'kuri/payments.html', context)


@login_required
@require_POST
def payment_update(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    form = PaymentEditForm(request.POST, instance=payment)
    if form.is_valid():
        form.save()
        messages.success(request, 'Payment updated successfully.')
    else:
        messages.error(request, 'Could not update payment. Please check the values.')
    next_url = request.POST.get('next') or 'payments'
    if next_url == 'member_detail':
        return redirect('member_detail', pk=payment.member.pk)
    return redirect('payments')


@login_required
@require_POST
def payment_ajax_update(request, pk):
    """Used by the 40-month tracking grid to cycle/set a payment's status via AJAX."""
    payment = get_object_or_404(Payment, pk=pk)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        data = request.POST

    new_status = data.get('status')
    valid_statuses = dict(Payment.STATUS_CHOICES)
    if new_status not in valid_statuses:
        return JsonResponse({'ok': False, 'error': 'Invalid status'}, status=400)

    payment.status = new_status
    if new_status == 'paid':
        payment.paid_date = date.today()
    else:
        payment.paid_date = None
    payment.save()

    member = payment.member
    return JsonResponse({
        'ok': True,
        'status': payment.status,
        'status_label': payment.get_status_display(),
        'member_total_paid': float(member.total_paid),
        'member_total_pending': float(member.total_pending),
        'member_months_paid': member.months_paid,
        'member_progress': member.payment_progress_percent,
    })


@login_required
def monthly_tracking(request):
    kuri = KuriScheme.objects.first()
    members = Member.objects.filter(kuri=kuri).order_by('member_id') if kuri else Member.objects.none()
    duration = kuri.duration_months if kuri else 40

    grid = []
    for member in members:
        payments = {p.month_number: p for p in member.payments.all()}
        row = {
            'member': member,
            'cells': [payments.get(m) for m in range(1, duration + 1)],
        }
        grid.append(row)

    context = {
        'kuri': kuri,
        'grid': grid,
        'months': range(1, duration + 1),
        'active_page': 'tracking',
    }
    return render(request, 'kuri/tracking.html', context)


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

@login_required
def collection(request):
    kuri = KuriScheme.objects.first()
    duration = kuri.duration_months if kuri else 40

    monthly_summary = []
    for m in range(1, duration + 1):
        month_payments = Payment.objects.filter(member__kuri=kuri, month_number=m)
        collected = month_payments.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0
        pending = month_payments.filter(status__in=['pending', 'overdue']).aggregate(total=Sum('amount'))['total'] or 0
        paid_count = month_payments.filter(status='paid').count()
        monthly_summary.append({
            'month': m,
            'collected': collected,
            'pending': pending,
            'paid_count': paid_count,
            'is_future': m > (kuri.current_month if kuri else 0),
        })

    total_collected = Payment.objects.filter(member__kuri=kuri, status='paid').aggregate(
        total=Sum('amount'))['total'] or 0
    total_pending = Payment.objects.filter(member__kuri=kuri, status__in=['pending', 'overdue']).aggregate(
        total=Sum('amount'))['total'] or 0

    context = {
        'kuri': kuri,
        'monthly_summary': monthly_summary,
        'total_collected': total_collected,
        'total_pending': total_pending,
        'active_page': 'collection',
    }
    return render(request, 'kuri/collection.html', context)


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

@login_required
def notifications(request):
    notes = Notification.objects.all()
    context = {'notifications': notes, 'active_page': 'notifications'}
    return render(request, 'kuri/notifications.html', context)


@login_required
@require_POST
def notification_mark_read(request, pk):
    note = get_object_or_404(Notification, pk=pk)
    note.is_read = True
    note.save()
    return redirect('notifications')


# ---------------------------------------------------------------------------
# Admin profile & settings
# ---------------------------------------------------------------------------

@login_required
def admin_profile(request):
    profile, _ = AdminProfile.objects.get_or_create(
        user=request.user,
        defaults={'name': 'Vishnu K', 'role': 'Administrator',
                  'location': 'Kerala, India', 'phone': '+91 90000 00000'},
    )
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('admin_profile')
    else:
        form = AdminProfileForm(instance=profile)
    return render(request, 'kuri/profile.html', {'profile': profile, 'form': form, 'active_page': 'profile'})


@login_required
def settings_view(request):
    kuri = KuriScheme.objects.first()
    if request.method == 'POST':
        kuri.name = request.POST.get('name', kuri.name)
        kuri.status = request.POST.get('status', kuri.status)
        kuri.current_month = int(request.POST.get('current_month', kuri.current_month))
        kuri.save()
        messages.success(request, 'Kuri settings updated successfully.')
        return redirect('settings')
    return render(request, 'kuri/settings.html', {'kuri': kuri, 'active_page': 'settings'})
