# Auth API Documentation

Base URL: `/auth`

## Overview

The Auth API provides authentication and user management endpoints. It handles user login and provides endpoints to retrieve current user information.

## Authentication & Authorization

- **Login Endpoint**: No authentication required
- **Current User Endpoint**: Requires JWT authentication via the `JwtGuard` and one of the following roles:
  - `SHIGURE_MASTER`
  - `SHIGURE_MANAGER`
  - `SHIGURE_USER`

---

## Endpoints

### 1. Login User

**Endpoint:** `POST /auth`

**Description:** Authenticate a user and return a JWT token.

**Required Roles:** None (Public endpoint)

**Headers:**
- `Content-Type: application/json`

**Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Request Example:**
```json
{
  "username": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
- `200 OK`: Authentication successful, returns user data and JWT token
```json
{
  "token": "jwt_token_string",
  "user": {
    "id": "user_id",
    "name": "user_name",
    "role": "SHIGURE_USER"
  }
}
```
- `401 Unauthorized`: Invalid credentials

---

### 2. Get Current User

**Endpoint:** `GET /auth`

**Description:** Retrieve information about the currently authenticated user.

**Required Roles:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`, `SHIGURE_USER`

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Request Example:**
```
GET /auth
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
- `200 OK`: Current user information
```json
{
  "id": "user_id",
  "name": "user_name",
  "role": "SHIGURE_USER",
  "level": "user_level"
}
```
- `401 Unauthorized`: Invalid or missing JWT token
- `403 Forbidden`: User does not have required roles

---

## Authentication Flow

1. **Login**: User sends credentials to `POST /auth`
2. **Token Received**: Server validates credentials and returns a JWT token
3. **Subsequent Requests**: Include the JWT token in the `Authorization` header as `Bearer <token>`
4. **Access Protected Endpoints**: Use the token to access authenticated endpoints like `/data/*`

## Token Format

The JWT token follows the standard format:
```
Header.Payload.Signature
```

- **Header**: Contains token type and signing algorithm
- **Payload**: Contains user information (id, name, role, etc.)
- **Signature**: Verifies the token's integrity

## Token Expiration

Tokens have a configured expiration time. When a token expires, the user must re-authenticate via the `POST /auth` endpoint to obtain a new token.
