from django.urls import path
from . import views

urlpatterns = [
    # Customers
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('api/customers/', views.customer_api_list, name='customer_api_list'),

    # Accounts
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/add/', views.account_create, name='account_create'),
    path('accounts/<int:pk>/', views.account_detail, name='account_detail'),
    path('accounts/<int:pk>/delete/', views.account_delete, name='account_delete'),

    # Transactions (deposit/withdraw)
    path('accounts/<int:account_pk>/transact/', views.transaction_create, name='transaction_create'),
]
