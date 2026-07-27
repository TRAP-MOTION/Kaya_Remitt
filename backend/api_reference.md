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

Payment lifecycle:

1. User creates a payment request → `AwaitingAcceptance`
2. Merchant accepts → `Accepted` (payable) or denies → `Denied`
3. User starts checkout on an accepted payment → `Pending` + `checkout_url`
4. After PayChangu payment, voucher generation verifies and marks → `COMPLETED`

---

## Create Payment

Creates a payment request for a selected merchant service. The request waits for merchant acceptance before checkout is allowed.

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
    "status": "AwaitingAcceptance"
  }
}
```

---

## Start Checkout

Initiates PayChangu checkout for an **Accepted** payment only.

### Endpoint

```http
POST /api/v1/payments/{payment_id}/checkout
```

### Response

```json
{
  "success": true,
  "message": "Checkout initiated successfully.",
  "data": {
    "payment_id": "PAY001",
    "status": "Pending",
    "checkout_url": "https://checkout.paychangu.com/923677185321"
  }
}
```

The frontend should redirect the user to `checkout_url` to complete payment on PayChangu.

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

If the payment is still `Pending` (checkout already started), the backend verifies the transaction with PayChangu using the stored `transaction_reference`. On success it marks the payment `COMPLETED`, simulates the merchant payout (sandbox), then issues the voucher.

Payments in `AwaitingAcceptance`, `Accepted`, or `Denied` cannot generate a voucher.

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
      "beneficiary_name": "Mary Banda",
      "service": "Grocery Package",
      "amount": 50000,
      "status": "AwaitingAcceptance"
    }
  ]
}
```

---

## Accept Payment

Merchant accepts a payment that is in `AwaitingAcceptance`. Once accepted, the diaspora user can start checkout.

### Endpoint

```http
PATCH /api/v1/merchant/payments/{payment_id}/accept
```

### Response

```json
{
  "success": true,
  "message": "Payment accepted successfully.",
  "data": {
    "payment_id": "PAY001",
    "status": "Accepted"
  }
}
```

The diaspora user receives a notification that the payment was accepted.

---

## Deny Payment

Merchant denies a payment that is in `AwaitingAcceptance`. Denied payments cannot be checked out.

### Endpoint

```http
PATCH /api/v1/merchant/payments/{payment_id}/deny
```

### Response

```json
{
  "success": true,
  "message": "Payment denied.",
  "data": {
    "payment_id": "PAY001",
    "status": "Denied"
  }
}
```

The diaspora user receives a notification that the payment was denied.

---

# 7. Notifications

User notification endpoints. Requires JWT authentication.

## List Notifications

Returns all notifications for the authenticated user, newest first.

### Endpoint

```http
GET /api/v1/notifications
```

### Response

```json
{
  "success": true,
  "data": [
    {
      "notification_id": "NOT001",
      "user_id": "USR001",
      "title": "Payment Accepted",
      "message": "Your payment of 50,000.00 to Chipiku Plus has been accepted. You can now proceed to checkout.",
      "category": "Payment",
      "is_read": false,
      "created_at": "2026-07-27T08:00:00Z"
    }
  ]
}
```

---

## Mark Notification as Read

Marks a single notification as read.

### Endpoint

```http
PATCH /api/v1/notifications/{notification_id}/read
```

### Response

```json
{
  "success": true,
  "message": "Notification marked as read.",
  "data": {
    "notification_id": "NOT001",
    "is_read": true
  }
}
```

---

## Mark All Notifications as Read

Marks all unread notifications for the authenticated user as read.

### Endpoint

```http
PATCH /api/v1/notifications/read-all
```

### Response

```json
{
  "success": true,
  "message": "All notifications marked as read."
}
```

---

# 8. User Profile

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

# 9. Admin Dashboard

Admin endpoints require JWT authentication and an account with the `admin` role.

Unauthorized or non-admin requests return:

```json
{
  "success": false,
  "message": "Access restricted to admin accounts."
}
```

---

## 9.1 Change Merchant Status

Updates a merchant's verification status.

Allowed `verification_status` values:

- `Pending`
- `Verified`
- `Rejected`
- `Suspended`

### Endpoint

```http
PATCH /api/v1/admin/merchants/{merchant_id}/status
```

### Request Body

```json
{
  "verification_status": "Verified",
  "reason": "Documents reviewed and approved."
}
```

| Field | Type | Required | Description |
|--------|------|----------|-------------|
| verification_status | string | Yes | New merchant status |
| reason | string | No | Optional admin note |

### Response

```json
{
  "success": true,
  "message": "Merchant status updated successfully.",
  "data": {
    "merchant_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "business_name": "Chipiku Plus",
    "verification_status": "Verified",
    "updated_at": "2026-07-26T17:00:00Z"
  }
}
```

---

## 9.2 Deactivate and Activate Accounts

Activates or deactivates a user account. Deactivated accounts cannot log in or access protected endpoints.

Allowed `account_status` values:

- `Active`
- `Inactive`

### Deactivate Account

### Endpoint

```http
PATCH /api/v1/admin/users/{user_id}/deactivate
```

### Request Body

```json
{
  "reason": "Suspicious activity reported."
}
```

| Field | Type | Required | Description |
|--------|------|----------|-------------|
| reason | string | No | Optional admin note |

### Response

```json
{
  "success": true,
  "message": "Account deactivated successfully.",
  "data": {
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "john@example.com",
    "account_status": "Inactive"
  }
}
```

---

### Activate Account

### Endpoint

```http
PATCH /api/v1/admin/users/{user_id}/activate
```

### Request Body

```json
{
  "reason": "Issue resolved. Account restored."
}
```

### Response

```json
{
  "success": true,
  "message": "Account activated successfully.",
  "data": {
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "john@example.com",
    "account_status": "Active"
  }
}
```

---

## 9.3 Warning Notifications

Sends a warning notification to a user. The notification is stored and delivered to the target account.

### Send Warning Notification

### Endpoint

```http
POST /api/v1/admin/warnings
```

### Request Body

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Account Warning",
  "message": "Multiple failed payment attempts were detected on your account. Further abuse may result in suspension."
}
```

| Field | Type | Required | Description |
|--------|------|----------|-------------|
| user_id | UUID | Yes | Target user |
| title | string | Yes | Warning title (max 150) |
| message | string | Yes | Warning body |

### Response

```json
{
  "success": true,
  "message": "Warning notification sent successfully.",
  "data": {
    "notification_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "title": "Account Warning",
    "message": "Multiple failed payment attempts were detected on your account. Further abuse may result in suspension.",
    "is_read": false,
    "created_at": "2026-07-26T17:05:00Z"
  }
}
```

---

### List Warning Notifications

Returns warning notifications sent by admins. Optional filter by user.

### Endpoint

```http
GET /api/v1/admin/warnings
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | UUID | No | Filter warnings for a specific user |

### Response

```json
{
  "success": true,
  "data": [
    {
      "notification_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "title": "Account Warning",
      "message": "Multiple failed payment attempts were detected on your account.",
      "is_read": false,
      "created_at": "2026-07-26T17:05:00Z"
    }
  ]
}
```

---

## 9.4 Support and Complaints

Allows admins to list, view, and resolve user support tickets and complaints.

Allowed ticket `status` values:

- `Open`
- `In Progress`
- `Resolved`
- `Closed`

Allowed ticket `category` values:

- `Support`
- `Complaint`
- `Payment`
- `Merchant`
- `Other`

---

### List Support Tickets

### Endpoint

```http
GET /api/v1/admin/support
```

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| status | string | No | Filter by ticket status |
| category | string | No | Filter by category |
| user_id | UUID | No | Filter by submitting user |

### Response

```json
{
  "success": true,
  "data": [
    {
      "ticket_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "category": "Complaint",
      "subject": "Merchant refused voucher",
      "status": "Open",
      "created_at": "2026-07-26T16:00:00Z",
      "updated_at": "2026-07-26T16:00:00Z"
    }
  ]
}
```

---

### Get Support Ticket Details

### Endpoint

```http
GET /api/v1/admin/support/{ticket_id}
```

### Response

```json
{
  "success": true,
  "data": {
    "ticket_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "category": "Complaint",
    "subject": "Merchant refused voucher",
    "description": "The merchant declined to honor a valid voucher code KAYA-A1B2C3.",
    "status": "Open",
    "admin_response": null,
    "created_at": "2026-07-26T16:00:00Z",
    "updated_at": "2026-07-26T16:00:00Z"
  }
}
```

---

### Update Support Ticket Status

Updates ticket status and optionally adds an admin response.

### Endpoint

```http
PATCH /api/v1/admin/support/{ticket_id}
```

### Request Body

```json
{
  "status": "Resolved",
  "admin_response": "We contacted the merchant and confirmed the voucher. Please try again."
}
```

| Field | Type | Required | Description |
|--------|------|----------|-------------|
| status | string | Yes | New ticket status |
| admin_response | string | No | Message shown to the user |

### Response

```json
{
  "success": true,
  "message": "Support ticket updated successfully.",
  "data": {
    "ticket_id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
    "status": "Resolved",
    "admin_response": "We contacted the merchant and confirmed the voucher. Please try again.",
    "updated_at": "2026-07-26T17:30:00Z"
  }
}
```

---

# 10. Security Features

KayaRemit API implements security practices including:

- JWT authentication.
- Password protection.
- Role-based access control.
- Merchant verification.
- Unique transaction identifiers.
- Voucher validation.
- Transaction logging.
- Secure API communication.
- Admin-only dashboard controls.

---

# 10. Future API Integrations

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
