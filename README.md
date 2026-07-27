# KayaRemit

KayaRemit is a secure web-based Direct-to-Merchant Digital Payment Platform designed to improve transparency and accountability in digital payments.

Instead of sending unrestricted cash, users can pay verified merchants directly for goods and services on behalf of family members, employees, or beneficiaries. Each payment generates a secure digital voucher that is verified by the merchant before goods or services are provided, ensuring payments are used for their intended purpose.

---

# Problem Statement

Current digital payment platforms successfully transfer money but provide no assurance that funds are used for their intended purpose. This creates a lack of transparency and accountability, especially when paying for essential goods and services on behalf of others.

KayaRemit addresses this challenge by enabling secure direct payments to verified merchants rather than unrestricted cash transfers.

---

# Features

### User

-User Registration
-Secure Login
-User Dashboard
-Profile Management
-Browse Verified Merchants
-View Merchant Services
-Direct Merchant Payments
-Digital Voucher Generation
-Transaction History

### Merchant

-Merchant Dashboard
-Business Profile Management
-Service Management
-Voucher Verification
-Payment Tracking

### Administrator

-User Management
-Merchant Approval
-Merchant Category Management
-Transaction Monitoring

---

# Technology Stack

## Frontend

-HTML5
-Tailwind CSS
-JavaScript

## Backend

-Python
-REST API

## Database

-PostgreSQL

## Payment Utility

-PayChangu

## Version Control

-Git
-GitHub

---

# System Architecture

```
                 Users
                    │
                    ▼
      Frontend (HTML • Tailwind • JavaScript)
                    │
                REST API
                    │
                    ▼
          Python Backend Application
                    │
                    ▼
          PostgreSQL Database
```

Detailed architecture is available in:

```
architecture.md
```

---

# Project Structure

```
Kaya_Remitt-main/
│
├── Frontend/
│   ├── assets/
│   ├── services/
│   │   └── api.js
│   ├── splash.html
│   ├── onboarding1.html
│   ├── onboarding2.html
│   ├── onboarding3.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── merchant-dashboard.html
│   └── admin-dashboard.html
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── seeds/
│   │   ├── utils/
│   │   ├── config.py
│   │   ├── extensions.py
│   │   └── __init__.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   ├── api_reference.md
│   ├── run.py
│   └── .env.example
│
├── docs/
│   ├── research.md
│   └── presentation.md
│
├── architecture.md
├── README.md
└── LICENSE
```

---

# Requirements

Before running KayaRemit, ensure you have:

-Python 3.10 or later
-PostgreSQL
-Git

---

# Installation

Clone the repository.

```bash
git clone https://github.com/your-username/KayaRemit.git

cd Kaya_Remitt-main
```

---

# Backend Setup

Navigate to the backend directory.

```bash
cd backend
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate the virtual environment.

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install project dependencies.

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

Create a `.env` file using `.env.example`.

Configure the required environment variables.

```
DATABASE_URL=
SECRET_KEY=
```

---

# Database Setup

Create a PostgreSQL database.

Run the required migrations or initialise the database before starting the application.

---

# Running the Backend

```bash
python run.py
```

The REST API will start locally.

---

# Running the Frontend

Open the `Frontend` directory and launch:

```
splash.html
```

or serve the folder using a local development server such as Live Server.

---

# Testing the Application

Suggested testing flow:

1.Register a user account.
2.Log in.
3.Browse verified merchants.
4.Select a merchant service.
5.Make a payment.
6.Generate a digital voucher.
7.Verify the voucher.
8.View transaction history.

---

# API Documentation

Detailed API documentation is available in:

```
backend/api_reference.md
```

---

# Documentation

Additional documentation can be found in the `docs` folder.

-Research
-Presentation
-System Architecture

---

# Project Status

**Current Version:** MVP (Minimum Viable Product)

The prototype demonstrates the complete payment workflow from user registration through merchant payment, voucher generation, voucher verification, and transaction tracking.

---

# License

This project is developed for educational and innovation purposes.