# KayaRemit

KayaRemit is a secure web-based Direct-to-Merchant Digital Payment Platform designed to improve transparency and accountability in financial transactions across Malawi. Instead of sending unrestricted cash, users can pay verified merchants directly for goods and services on behalf of family members, friends, employees, or beneficiaries.

The platform ensures that payments are used for their intended purpose by generating secure digital vouchers that are verified by merchants before goods or services are redeemed.

---

## Problem Statement

Many people send money for groceries, school fees, medical bills, utility payments, farming inputs, and construction materials. Once the money is transferred, there is often no assurance that it will be used as intended.

This challenge affects both people living within Malawi and Malawians living abroad who support their families.

KayaRemit addresses this problem by enabling users to pay verified merchants directly instead of transferring unrestricted cash.

---

## Solution

KayaRemit provides a secure digital payment platform where users can:

-Register and manage an account.
-Browse verified merchants.
-Select goods or services.
-Make direct merchant payments.
-Receive secure digital vouchers.
-Track payment history.
-Redeem vouchers through verified merchants.

---

## Key Features

### User Features

-User Registration
-Secure Login
-User Dashboard
-Profile Management
-Merchant Directory
-Merchant Categories
-Service Catalogue
-Direct Merchant Payments
-Digital Voucher Generation
-Transaction History
-Notifications

### Merchant Features

-Merchant Registration
-Business Profile Management
-Service Management
-Voucher Verification
-Payment History

### Administrator Features

-User Management
-Merchant Approval
-Category Management
-Transaction Monitoring
-Platform Management

---

## Technology Stack

### Frontend

-HTML5
-Tailwind CSS
-JavaScript

### Backend

-Python

### Database

-PostgreSQL

### Version Control

-Git
-GitHub

---

## System Architecture

The platform follows a three-tier architecture:

Presentation Layer
-HTML
-Tailwind CSS
-JavaScript

Application Layer
-Python REST API
-Business Logic
-Authentication
-Voucher Management

Data Layer
-PostgreSQL Database

---

## Project Structure

```
KayaRemit/
│
├── frontend/
│   ├── assets/
│   ├── css/
│   ├── js/
│   ├── pages/
│   └── index.html
│
├── backend/
│   ├── app/
│   ├── api/
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── database/
│   └── schema.sql
│
├── docs/
│   ├── API.md
│   ├── DATABASE.md
│   ├── ARCHITECTURE.md
│   ├── BUSINESS_MODEL.md
│   └── RESEARCH.pdf
│
├── README.md
└── LICENSE
```

---

## Database

PostgreSQL

Main Tables

-Users
-Merchant Categories
-Merchants
-Services
-Payments
-Vouchers
-Transactions
-Notifications

---

## Security

KayaRemit implements several security measures, including:

-Password Hashing
-JWT Authentication
-Role-Based Access Control
-Secure Voucher Verification
-Transaction Logging
-Unique Transaction References
-Input Validation

---

## Future Enhancements

-Mobile Money Integration
-Banking Integration
-QR Code Payments
-Mobile Application
-SMS Notifications
-Email Notifications
-Merchant Analytics
-AI Fraud Detection
-Multi-Currency Support
-International Payment Support

---

## Documentation

Project documentation includes:

-Research Report
-API Documentation
-Database Design
-System Architecture
-Business Model
-Pitch Deck

---

## Project Status

Current Version: MVP (Minimum Viable Product)

This prototype demonstrates the core functionality of KayaRemit, including secure authentication, merchant management, direct merchant payments, voucher generation, and transaction tracking.

---

## Team

KayaRemit Development Team

-Frontend Development
-Backend Development
-Database Design
-Research
-Documentation
-UI/UX Design

