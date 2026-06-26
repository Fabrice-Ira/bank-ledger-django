from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction as db_transaction
from django.db.models import Q
from .models import Customer, Account, Transaction
from .forms import CustomerForm, AccountForm, TransactionForm
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerSerializer

# ---------- CUSTOMER CRUD ----------

@login_required
def customer_list(request):
    query = request.GET.get('q', '')
    customers = Customer.objects.all()
    if query:
        customers = customers.filter(
            Q(full_name__icontains=query) | Q(national_id__icontains=query)
        )
    return render(request, 'ledger/customer_list.html', {
        'customers': customers, 'query': query
    })


@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully.')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'ledger/customer_form.html', {'form': form})


@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated.')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'ledger/customer_form.html', {'form': form})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted.')
        return redirect('customer_list')
    return render(request, 'ledger/customer_confirm_delete.html', {'customer': customer})


# ---------- ACCOUNT CRUD ----------

@login_required
def account_list(request):
    query = request.GET.get('q', '')
    accounts = Account.objects.select_related('customer').all()
    if query:
        accounts = accounts.filter(
            Q(account_number__icontains=query) |
            Q(customer__full_name__icontains=query)
        )
    return render(request, 'ledger/account_list.html', {
        'accounts': accounts, 'query': query
    })


@login_required
def account_create(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully.')
            return redirect('account_list')
    else:
        form = AccountForm()
    return render(request, 'ledger/account_form.html', {'form': form})


@login_required
def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk)
    transactions = account.transactions.order_by('-timestamp')
    return render(request, 'ledger/account_detail.html', {
        'account': account, 'transactions': transactions
    })


@login_required
def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == 'POST':
        account.delete()
        messages.success(request, 'Account deleted.')
        return redirect('account_list')
    return render(request, 'ledger/account_confirm_delete.html', {'account': account})


# ---------- TRANSACTIONS: DEPOSIT / WITHDRAW ----------

@login_required
def transaction_create(request, account_pk):
    """
    Creates a Transaction AND updates the Account balance atomically.
    This is the core business logic of the whole project.
    """
    account = get_object_or_404(Account, pk=account_pk)

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            ttype = form.cleaned_data['transaction_type']

            if ttype == 'withdraw' and amount > account.balance:
                messages.error(request, 'Insufficient balance for this withdrawal.')
                return redirect('account_detail', pk=account.pk)

            with db_transaction.atomic():
                txn = form.save(commit=False)
                txn.account = account
                txn.save()

                if ttype == 'deposit':
                    account.balance += amount
                else:  # withdraw
                    account.balance -= amount
                account.save()

            messages.success(request, f'{ttype.capitalize()} of {amount} recorded.')
            return redirect('account_detail', pk=account.pk)
    else:
        form = TransactionForm(initial={'account': account})

    return render(request, 'ledger/transaction_form.html', {
        'form': form, 'account': account
    })
# ---------- DRF API ENDPOINT ----------

@api_view(['GET', 'POST'])
def customer_api_list(request):
    if request.method == 'GET':
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
