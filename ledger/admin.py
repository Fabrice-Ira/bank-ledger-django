from django.contrib import admin
from .models import Customer, Account, Transaction


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'national_id', 'phone_number', 'date_joined')
    search_fields = ('full_name', 'national_id')


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'customer', 'account_type', 'balance')
    list_filter = ('account_type',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'amount', 'timestamp')
    list_filter = ('transaction_type',)
