# Bank Account & Transaction Ledger

A Django web application implementing a banking system with Customers, Accounts, and Transactions, deployed with MySQL, Nginx, and Gunicorn on Ubuntu Server.

## Entity Relationships
- Customer → Account (One-to-Many)
- Account → Transaction (One-to-Many)

## Features
- Full CRUD for Customers and Accounts via custom HTML/CSS/JS frontend
- Deposit/Withdraw transactions with automatic, atomic balance updates
- Insufficient-balance validation on withdrawals
- File uploads: KYC document, profile picture
- Search by name / national ID / account number
- Login-protected views (Django auth)
- REST API endpoint: GET/POST `/ledger/api/customers/` (Django REST Framework)
- Deployed behind Nginx (reverse proxy + static files) with Gunicorn (WSGI server)

## Setup
1. Clone the repo: `git clone <your-repo-url>`
2. Create virtual environment: `python3 -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Configure MySQL database in `core/settings.py`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Run dev server: `python manage.py runserver`
   Or run production: `gunicorn --bind 127.0.0.1:8000 core.wsgi:application` behind Nginx

## Tech Stack
Django · Django REST Framework · MySQL · Nginx · Gunicorn · Ubuntu Server
