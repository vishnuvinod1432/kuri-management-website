from django import forms
from .models import Member, Payment, AdminProfile


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'member_id', 'name', 'phone', 'email', 'date_of_birth',
            'address', 'joining_date', 'monthly_amount', 'is_active',
        ]
        widgets = {
            'member_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. KM021'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9xxxxxxxxx'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'joining_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'monthly_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PaymentEditForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['status', 'amount', 'due_date', 'paid_date', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'paid_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional note'}),
        }


class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ['name', 'role', 'location', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
