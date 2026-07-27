# KayaRemit

KayaRemit is a secure web-based Direct-to-Merchant Digital Payment Platform that improves transparency and accountability in digital payments.

Instead of sending unrestricted cash, KayaRemit allows users to make payments directly to verified merchants for specific goods and services. The platform generates digital vouchers that merchants can verify before providing services, ensuring that payments are used for their intended purpose.

---

# Problem Statement

Many individuals send money for essential needs such as groceries, education, healthcare, utilities, farming inputs, and construction materials. However, after funds are transferred, senders often have no visibility or assurance that the money was used as intended.

This creates challenges including:

-Lack of transparency
-Limited accountability
-Risk of misuse
-Reduced trust in digital payments

KayaRemit solves this by connecting users directly with verified merchants instead of sending unrestricted cash.

---

# Solution

KayaRemit provides a secure digital payment ecosystem where users can:

-Create accounts
-Browse verified merchants
-Select available services
-Make direct payments
-Receive digital vouchers
-Verify transactions
-Track payment history

---

# Key Features

## User Features

-User Registration
-Secure Login
-User Profile Management
-Merchant Discovery
-Merchant Categories
-Service Selection
-Direct Merchant Payments
-Digital Voucher Generation
-Transaction History

## Merchant Features

-Merchant Dashboard
-Merchant Profile Management
-Service Management
-Voucher Verification
-Payment Tracking

## Administrator Features

-User Management
-Merchant Management
-Transaction Monitoring
-Platform Administration

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

## Development Tools

-Git
-GitHub

## Payment Integration

-PayChangu Payment Utility

---

# System Architecture

KayaRemit follows a three-layer architecture:

```
                 Users
                   |
                   |
          Frontend Layer
     HTML + Tailwind + JavaScript
                   |
                   |
              REST API
                   |
                   |
          Backend Layer
              Python
                   |
                   |
        PostgreSQL Database
```

---

# Project Structure

```
Kaya_Remitt-main/

│
├── Frontend/
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
│   │
│   ├── app/
│   │   ├── models/
│   │   │   ├── users.py
│   │   │   ├── merchant.py
│   │   │   ├── payment.py
│   │   │   ├── voucher.py
│   │   │   ├── transaction.py
│   │   │   └── notification.py
│   │   │
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── merchants.py
│   │   │   ├── payments.py
│   │   │   └── vouchers.py
│   │   │
│   │   ├── schemas/
│   │   ├── utils/
│   │   └── config.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── run.py
│
├── docs/
│   ├── research.md
│   └── presentation.md
│
├── architecture.md
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/your-team/KayaRemit.git

cd KayaRemit
```

---

# Backend Setup

Navigate to backend:

```bash
cd backend
```

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Database Setup

KayaRemit uses PostgreSQL.

Create a PostgreSQL database and configure environment variables.

Create a `.env` file using:

```
backend/.env.example
```

Required configuration:

```
DATABASE_URL=
SECRET_KEY=
```

---

# Running the Backend

From the backend directory:

```bash
python run.py
```

The API server will start locally.

---

# Running the Frontend

Open the frontend folder:

```
Frontend/
```

Launch:

```
splash.html
```

or run using a local development server.

---

# API Modules

The backend provides REST endpoints for:

-Authentication
-User Management
-Merchant Management
-Payments
-Voucher Generation
-Transaction Management

Full API documentation:

```
backend/api_reference.md
```

---

# Testing

The project includes automated backend tests.

Run:

```bash
pytest
```

Test coverage includes:

-Authentication
-Users
-Merchants
-Payments
-Vouchers
-Validation

---

# Database Models

Main entities:

-Users
-Merchants
-Merchant Categories
-Services
-Payments
-Vouchers
-Transactions
-Notifications

---

# Future Improvements

Planned improvements:

-Mobile Money Integration
-Banking Integration
-QR Code Payments
-Mobile Application
-SMS Notifications
-Merchant Analytics
-AI Fraud Detection

---

# Project Status

Current Version:

```
MVP (Minimum Viable Product)
```

The prototype demonstrates the complete KayaRemit workflow:

User Registration → Merchant Selection → Payment → Voucher Generation → Merchant Verification → Transaction Tracking

---

# License

This project is developed for innovation and educational purposes.