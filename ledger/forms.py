from django import forms
from .models import Customer, Account, Transaction


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'national_id', 'phone_number', 'address',
                  'kyc_document', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['customer', 'account_number', 'account_type', 'balance']
        # 'customer' auto-renders as a <select> dropdown because it's a ForeignKey


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['account', 'transaction_type', 'amount', 'description']
        # 'account' also auto-renders as a dropdown
