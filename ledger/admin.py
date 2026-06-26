from django.contrib import admin
from .models import Customer, Account, Transaction


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'national_id', 'phone_number', 'date_joined')
    search_fields = ('full_name', 'national_id')

