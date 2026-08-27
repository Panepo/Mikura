# Project API Documentation

## Overview
This document describes the Project API endpoints for the Shigure backend application. The Project API allows users to manage projects including listing, retrieving, updating, and adding virtual projects.

## Base URL
```
/project
```

## Authentication
All endpoints require authentication via JWT token and are protected by the `JwtGuard`.

## Roles and Permissions
- **SHIGURE_MASTER**: Full access to all project operations
- **SHIGURE_MANAGER**: Access to most project operations (with some restrictions)
- **SHIGURE_USER**: Read-only access to project data

---

## Endpoints

### 1. List All Projects
**Endpoint:** `GET /project`

**Description:** Retrieves a list of all projects based on the provided query parameters.

**Authentication:** Required (JWT)

**Roles Allowed:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`, `SHIGURE_USER`

**Query Parameters:**
- Supports various query parameters for filtering and pagination (flattened query format)

**Response:**
```json
{
  "data": [
    {
      "id": "string",
      "name": "string",
      "code": "string",
      "captain": "string",
      "keeper": "string",
      "unit": number,
      "shortcut": boolean,
      "upload": boolean,
      "virtual": boolean,
      "hidden": boolean
    }
  ],
  "total": number,
  "has_more": boolean
}
```

---

### 2. Get Single Project
**Endpoint:** `GET /project/:prjName`

**Description:** Retrieves a specific project by its name. If the project name is `SHORTCUT`, it returns a list of shortcut projects.

**Authentication:** Required (JWT)

**Roles Allowed:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`, `SHIGURE_USER`

**Path Parameters:**
- `prjName` (string): The name of the project to retrieve

**Special Cases:**
- If `prjName` is `SHORTCUT`, returns shortcut projects

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "code": "string",
  "captain": "string",
  "keeper": "string",
  "unit": number,
  "shortcut": boolean,
  "upload": boolean,
  "virtual": boolean,
  "hidden": boolean
}
```

---

### 3. Query Projects
**Endpoint:** `GET /project/query/:name`

**Description:** Searches for projects based on the provided name, code, or captain information.

**Authentication:** Required (JWT)

**Roles Allowed:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`

**Path Parameters:**
- `name` (string): The search term for project name, code, or captain

**Response:**
```json
{
  "data": [
    {
      "name": "string",
      "code": "string",
      "captain": "string"
    }
  ]
}
```

---

### 4. Update Project
**Endpoint:** `PATCH /project/:id`

**Description:** Updates an existing project with the provided information.

**Authentication:** Required (JWT)

**Roles Allowed:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`

**Path Parameters:**
- `id` (string): The ObjectId of the project to update

**Request Body (UpdateProjectDto):**
```json
{
  "keeperNo": "string",
  "unit": "string",
  "shortcut": boolean,
  "upload": boolean,
  "hidden": boolean
}
```

**Response:**
```json
{
  "message": "Project updated successfully"
}
```

**Status Codes:**
- `200`: Project updated successfully

---

### 5. Reload Project Data
**Endpoint:** `PATCH /project/data/:code`

**Description:** Reloads project data for a specific project code.

**Authentication:** Required (JWT)

**Roles Allowed:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`

**Path Parameters:**
- `code` (string): The project code to reload

**Response:**
```json
{
  "message": "Project reloaded successfully"
}
```

**Status Codes:**
- `200`: Project reloaded successfully

---

### 6. Add Virtual Project
**Endpoint:** `POST /project`

**Description:** Adds a new virtual project.

**Authentication:** Required (JWT)

**Roles Allowed:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`

**Request Body (AddVirtualDto):**
```json
{
  "name": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "code": "string",
  "captain": "string",
  "keeper": "string",
  "unit": number,
  "shortcut": boolean,
  "upload": boolean,
  "virtual": boolean,
  "hidden": boolean
}
```

---

## Data Models

### ProjectDto
```typescript
interface ProjectDto {
  id: string;
  name: string;
  code: string;
  captain: string;
  keeper: string;
  unit: number;
  shortcut: boolean;
  upload: boolean;
  virtual: boolean;
  hidden: boolean;
}
```

### UpdateProjectDto
```typescript
interface UpdateProjectDto {
  keeperNo?: string;
  unit?: string;
  shortcut?: boolean;
  upload?: boolean;
  hidden?: boolean;
}
```

### AddVirtualDto
```typescript
interface AddVirtualDto {
  name: string;
}
```

### QueryProjectDto
```typescript
interface QueryProjectDto {
  name: string;
  code: string;
  captain: string;
}
```

---

## Error Handling

All endpoints may return the following standard HTTP status codes:

- `401 Unauthorized`: When authentication is missing or invalid
- `403 Forbidden`: When the user does not have the required role
- `404 Not Found`: When the requested project does not exist
- `400 Bad Request`: When the request body or parameters are invalid
- `500 Internal Server Error`: When an unexpected server error occurs

---

## Notes

- All project-related endpoints use the `JwtGuard` for authentication
- Role-based access control is implemented using the `@Roles()` decorator
- Query parameters are flattened using the `unflattenQuery` helper function
- Virtual projects are created with the `addVirtual` method
- Project data can be reloaded using the `reload` method with project codes
