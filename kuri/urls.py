from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('members/', views.members_list, name='members'),
    path('members/add/', views.member_add, name='member_add'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    path('members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('members/<int:pk>/delete/', views.member_delete, name='member_delete'),

    path('payments/', views.payments_list, name='payments'),
    path('payments/<int:pk>/update/', views.payment_update, name='payment_update'),
    path('payments/<int:pk>/ajax-update/', views.payment_ajax_update, name='payment_ajax_update'),

    path('tracking/', views.monthly_tracking, name='tracking'),
    path('collection/', views.collection, name='collection'),

    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:pk>/read/', views.notification_mark_read, name='notification_mark_read'),

    path('profile/', views.admin_profile, name='admin_profile'),
    path('settings/', views.settings_view, name='settings'),
]
