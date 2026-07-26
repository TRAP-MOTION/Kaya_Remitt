# KayaRemit

## Direct-to-Merchant Diaspora Payment Platform for Malawi

KayaRemit is a web-based fintech platform designed to improve how Malawians living abroad support their families back home.

Instead of sending unrestricted cash, KayaRemit enables diaspora users to make direct payments to verified local merchants and service providers. This creates a safer, more transparent, and accountable way of supporting essential needs such as groceries, medical services, school payments, and other necessities.

---

# Problem

Many Malawians living abroad send money home to support their families. However, traditional remittance methods provide limited visibility into how the money is used after it has been transferred.

Challenges include:

-Limited control over how funds are spent.
-Lack of transparency after payments are made.
-Difficulty confirming whether financial support reached its intended purpose.
-Limited connection between diaspora users and local service providers.

KayaRemit addresses this challenge by connecting diaspora users directly with verified merchants.

---

# Solution

KayaRemit allows users to:

1.Create an account.
2.Browse verified merchants.
3.Select a product or service.
4.Complete a digital payment.
5.Receive a secure digital voucher.
6.Allow merchants to verify and redeem the voucher.

This ensures that financial support is directed toward its intended purpose.

---

# Core Features

## User Features

-User registration and authentication.
-Browse verified merchants.
-View available services.
-Create payment requests.
-Generate digital vouchers.
-View payment history.

## Merchant Features

-Merchant profile management.
-View received payments.
-Verify digital vouchers.
-Redeem completed transactions.

## Security Features

-JWT authentication.
-Role-based access control.
-Unique transaction references.
-Voucher validation.
-Transaction records.

---

# System Workflow

```
Diaspora User

        ↓

Register / Login

        ↓

Browse Verified Merchants

        ↓

Select Service

        ↓

Confirm Payment

        ↓

Generate Digital Voucher

        ↓

Merchant Verifies Voucher

        ↓

Service Provided

        ↓

Transaction Completed
```

---

# Technology Stack

## Frontend

-HTML
-Tailwind CSS
-JavaScript

## Backend

-Python

## Database

-PostgreSQL

## Authentication

-JWT

## Version Control

-Git

---

# Project Structure

```
KayaRemit/

├── frontend/
│   ├── pages/
│   ├── assets/
│   └── components/
│
├── backend/
│   ├── api/
│   ├── models/
│   ├── services/
│   └── database/
│
├── docs/
│   ├── PROJECT_RESEARCH.md
│   └── API.md
│
└── README.md
```

---

# API Documentation

The backend API documentation can be found here:

```
backend/app/
```

It includes:

-Authentication endpoints.
-Merchant endpoints.
-Payment endpoints.
-Voucher verification endpoints.
-Transaction management.

---

# Database Design

The system uses PostgreSQL to manage:

-Users.
-Merchants.
-Services.
-Payments.
-Transactions.
-Digital vouchers.

---

# Future Improvements

Future versions of KayaRemit may include:

-Mobile money integration.
-Banking integrations.
-International payment gateways.
-Mobile applications.
-AI-powered fraud detection.
-Advanced merchant analytics.

---

# Project Vision

KayaRemit aims to create a more transparent and trusted way for diaspora communities to support families and businesses in Malawi.

By connecting people abroad with verified local merchants, KayaRemit demonstrates how digital technology can improve financial inclusion and accountability.

---

# Contributors

-Product Designer
-Backend Developer
-Frontend Developer
-Researcher
-Communications Lead
