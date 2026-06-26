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

from .serializers import AccountSerializer


@api_view(['GET'])
def account_balance_api(request, pk):
    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'account_number': account.account_number,
        'customer': account.customer.full_name,
        'balance': account.balance
    })

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
#-----
@login_required
def account_update(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == 'POST':
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account updated.')
            return redirect('account_list')
    else:
        form = AccountForm(instance=account)
    return render(request, 'ledger/account_form.html', {'form': form})

# --------
def about(request):
    return render(request, 'ledger/about.html')


def home(request):
    """
    Homepage: simple balance lookup tool.
    """
    account = None
    error = None
    account_number = request.GET.get('account_number')

    if account_number:
        try:
            account = Account.objects.get(account_number=account_number)
        except Account.DoesNotExist:
            error = f"No account found with number '{account_number}'."

    return render(request, 'ledger/home.html', {
        'account': account, 'error': error, 'account_number': account_number or ''
    })

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
from datetime import datetime


@login_required
def transaction_list(request):
    transactions = Transaction.objects.select_related('account', 'account__customer').order_by('-timestamp')

    account_number = request.GET.get('account_number', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if account_number:
        transactions = transactions.filter(account__account_number__icontains=account_number)

    if date_from:
        try:
            parsed_from = datetime.strptime(date_from, '%Y-%m-%d')
            transactions = transactions.filter(timestamp__date__gte=parsed_from.date())
        except ValueError:
            pass

    if date_to:
        try:
            parsed_to = datetime.strptime(date_to, '%Y-%m-%d')
            transactions = transactions.filter(timestamp__date__lte=parsed_to.date())
        except ValueError:
            pass

    return render(request, 'ledger/transaction_list.html', {
        'transactions': transactions,
        'account_number': account_number,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
def transaction_update(request, pk):
    """
    Editing a transaction must correctly reverse the OLD effect on the
    account balance, then apply the NEW effect — otherwise the balance
    would drift out of sync with the transaction history.
    """
    txn = get_object_or_404(Transaction, pk=pk)
    account = txn.account

    old_amount = txn.amount
    old_type = txn.transaction_type

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=txn)
        if form.is_valid():
            new_amount = form.cleaned_data['amount']
            new_type = form.cleaned_data['transaction_type']

            with db_transaction.atomic():
                # Step 1: reverse the OLD effect
                if old_type == 'deposit':
                    account.balance -= old_amount
                else:
                    account.balance += old_amount

                # Step 2: validate the NEW effect before applying it
                if new_type == 'withdraw' and new_amount > account.balance:
                    messages.error(request, 'Insufficient balance for this edit (would go negative).')
                    return redirect('transaction_list')

                # Step 3: apply the NEW effect
                if new_type == 'deposit':
                    account.balance += new_amount
                else:
                    account.balance -= new_amount

                account.save()
                form.save()

            messages.success(request, 'Transaction updated and balance corrected.')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=txn)

    return render(request, 'ledger/transaction_form.html', {
        'form': form, 'account': account, 'editing': True
    })


@login_required
def transaction_delete(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)
    account = txn.account

    if request.method == 'POST':
        with db_transaction.atomic():
            # Reverse this transaction's effect on the balance before deleting it
            if txn.transaction_type == 'deposit':
                account.balance -= txn.amount
            else:
                account.balance += txn.amount
            account.save()
            txn.delete()

        messages.success(request, 'Transaction deleted and balance corrected.')
        return redirect('transaction_list')

    return render(request, 'ledger/transaction_confirm_delete.html', {'transaction': txn})
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
