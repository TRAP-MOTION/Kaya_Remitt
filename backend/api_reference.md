# KayaRemit API Documentation

## Overview

The KayaRemit API provides backend services for the Direct-to-Merchant Diaspora Payment Platform.

The API allows diaspora users to create accounts, browse verified merchants, select services, create payments, generate digital vouchers, and enable merchants to verify transactions.

## Base URL

```
/api/v1
```

## Authentication

Protected endpoints require JWT authentication.

Header:

```http
Authorization: Bearer <access_token>
```

---

# Response Format

## Success Response

```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": {}
}
```

## Error Response

```json
{
  "success": false,
  "message": "An error occurred."
}
```

---

# 1. Authentication

## Register User

Creates a new KayaRemit account.

### Endpoint

```http
POST /api/v1/auth/register
```

### Request Body

```json
{
  "full_name": "John Banda",
  "email": "john@example.com",
  "password": "password123",
  "role": "diaspora"
}
```

### Response

```json
{
  "success": true,
  "message": "Account created successfully.",
  "data": {
    "user_id": "USR001",
    "role": "diaspora"
  }
}
```

---

## Login

Authenticates a user and provides access to the platform.

### Endpoint

```http
POST /api/v1/auth/login
```

### Request Body

```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

### Response

```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "token": "jwt_token_here"
  }
}
```

---

# 2. Merchant Management

## Get Verified Merchants

Returns a list of available verified merchants.

### Endpoint

```http
GET /api/v1/merchants
```

### Response

```json
{
  "success": true,
  "data": [
    {
      "merchant_id": "MER001",
      "business_name": "Chipiku Plus",
      "category": "Groceries",
      "location": "Lilongwe",
      "verified": true
    }
  ]
}
```

---

## Get Merchant Details

Retrieves details of a specific merchant.

### Endpoint

```http
GET /api/v1/merchants/{merchant_id}
```

### Response

```json
{
  "success": true,
  "data": {
    "merchant_id": "MER001",
    "business_name": "Chipiku Plus",
    "services": [
      {
        "name": "Grocery Package",
        "price": 50000
      }
    ]
  }
}
```

---

# 3. Services

## Get Merchant Services

Returns available products or services from a merchant.

### Endpoint

```http
GET /api/v1/merchants/{merchant_id}/services
```

### Response

```json
{
  "success": true,
  "data": [
    {
      "service_id": "SER001",
      "name": "Grocery Package",
      "amount": 50000
    }
  ]
}
```

---

# 4. Payments

## Create Payment

Creates a payment request for a selected merchant service.

### Endpoint

```http
POST /api/v1/payments
```

### Request Body

```json
{
  "merchant_id": "MER001",
  "service_id": "SER001",
  "beneficiary_name": "Mary Banda",
  "amount": 50000
}
```

### Response

```json
{
  "success": true,
  "message": "Payment created successfully.",
  "data": {
    "payment_id": "PAY001",
    "status": "Pending",
    "checkout_url": "https://checkout.paychangu.com/923677185321"
  }
}
```

The frontend should redirect the user to `checkout_url` to complete payment on PayChangu. Payment status becomes `COMPLETED` only after PayChangu verification during voucher generation.

---

## Get Payment History

Returns previous payments made by the user.

### Endpoint

```http
GET /api/v1/payments/history
```

### Response

```json
{
  "success": true,
  "data": [
    {
      "payment_id": "PAY001",
      "merchant": "Chipiku Plus",
      "amount": 50000,
      "status": "COMPLETED"
    }
  ]
}
```

---

# 5. Digital Voucher System

## Generate Voucher

Creates a digital voucher after successful payment.

If the payment is still `Pending`, the backend verifies the transaction with PayChangu using the stored `transaction_reference`. On success it marks the payment `COMPLETED`, simulates the merchant payout (sandbox), then issues the voucher.

### Endpoint

```http
POST /api/v1/vouchers
```

### Request Body

```json
{
  "payment_id": "PAY001"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "voucher_id": "KAYA-001245",
    "status": "ACTIVE",
    "merchant": "Chipiku Plus",
    "amount": 50000
  }
}
```

---

## Verify Voucher

Allows merchants to check whether a voucher is valid.

### Endpoint

```http
POST /api/v1/vouchers/verify
```

### Request Body

```json
{
  "voucher_id": "KAYA-001245"
}
```

### Response

```json
{
  "success": true,
  "message": "Voucher verified successfully.",
  "data": {
    "status": "VALID",
    "amount": 50000,
    "merchant": "Chipiku Plus"
  }
}
```

---

## Redeem Voucher

Marks a voucher as used after the customer receives goods or services.

### Endpoint

```http
PATCH /api/v1/vouchers/{voucher_id}/redeem
```

### Response

```json
{
  "success": true,
  "message": "Voucher redeemed successfully.",
  "data": {
    "status": "REDEEMED"
  }
}
```

---

# 6. Merchant Dashboard

## View Merchant Transactions

Returns payments received by a merchant.

### Endpoint

```http
GET /api/v1/merchant/transactions
```

### Response

```json
{
  "success": true,
  "data": [
    {
      "transaction_id": "PAY001",
      "amount": 50000,
      "status": "REDEEMED"
    }
  ]
}
```

---

# 7. User Profile

## Get User Profile

Retrieves user information.

### Endpoint

```http
GET /api/v1/profile
```

---

## Update User Profile

Updates user details.

### Endpoint

```http
PUT /api/v1/profile
```

---

# 8. Security Features

KayaRemit API implements security practices including:

- JWT authentication.
- Password protection.
- Role-based access control.
- Merchant verification.
- Unique transaction identifiers.
- Voucher validation.
- Transaction logging.
- Secure API communication.

---

# 9. Future API Integrations

Future versions may include:

- Mobile money APIs.
- Banking APIs.
- Payment gateway integrations.
- AI-powered fraud detection.
- Merchant analytics services.

---

# Technology Stack

## Backend

Python

## Database

PostgreSQL

## Authentication

JWT

## Frontend

HTML  
Tailwind CSS  
JavaScript

## Version Control

GitHub