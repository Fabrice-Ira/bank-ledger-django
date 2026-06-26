from rest_framework import serializers
from .models import Customer, Account, Transaction


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'full_name', 'national_id', 'phone_number', 'address', 'date_joined']


class AccountSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)

    class Meta:
        model = Account
        fields = ['id', 'customer', 'customer_name', 'account_number', 'account_type', 'balance']
