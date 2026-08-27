# Data API Documentation

Base URL: `/data`

## Overview

The Data API provides endpoints for managing various data types including Drivers, BIOS, EC, and Applications. It supports file uploads, downloads, and CRUD operations for different data tables.

## Authentication & Authorization

All `/data` endpoints (except where noted) require JWT authentication via the `JwtGuard`. Roles required vary by endpoint:

- **SHIGURE_MASTER**: Full access to all data operations
- **SHIGURE_MANAGER**: Full access to all data operations
- **SHIGURE_USER**: Read-only access to data retrieval operations

---

## Endpoints

### 1. Upload Single File

**Endpoint:** `POST /data/upload/:id`

**Description:** Upload a single file for a specific data ID and type.

**Required Roles:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`

**Headers:**
- `Authorization: Bearer <jwt_token>`
- `Content-Type: multipart/form-data`

**Path Parameters:**
| Parameter | Type   | Description              |
|-----------|--------|--------------------------|
| `id`      | string | The target data ID       |

**Body (multipart/form-data):**
| Field  | Type   | Description                    |
|--------|--------|--------------------------------|
| `file` | file   | The file to upload             |
| `type` | string | The type of data being uploaded|

**Response:**
- `200 OK`: `{ "message": "File uploaded successfully" }`
- `400 Bad Request`: `{ "message": "File is required" }`

---

### 2. Upload Multiple Files

**Endpoint:** `POST /data/uploads/:id`

**Description:** Upload multiple files for a specific data ID with detailed upload configuration.

**Required Roles:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`

**Headers:**
- `Authorization: Bearer <jwt_token>`
- `Content-Type: multipart/form-data`

**Path Parameters:**
| Parameter | Type   | Description              |
|-----------|--------|--------------------------|
| `id`      | string | The target data ID       |

**Body (multipart/form-data):**
| Field  | Type                | Description                    |
|--------|---------------------|--------------------------------|
| `file` | file                | The file to upload             |
| `type` | string              | The type of data being uploaded|
| `name` | string              | File name                      |
| `size` | number              | File size                      |
| `date` | string (ISO 8601)   | Upload date                    |

**Response:**
- `200 OK`: `{ "message": "File uploaded successfully" }`
- `400 Bad Request`: `{ "message": "File is required" }`

---

### 3. Download Data

**Endpoint:** `POST /data/download/:table/:id`

**Description:** Download data for a specific table and ID.

**Required Roles:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`, `SHIGURE_USER`

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Path Parameters:**
| Parameter | Type   | Description              |
|-----------|--------|--------------------------|
| `table`   | string | The data table name        |
| `id`      | string | The target data ID         |

**Body:**
| Field  | Type   | Description              |
|--------|--------|--------------------------|
| `type` | string | The type of data to download|

**Response:**
- `200 OK`: Downloaded data or file stream

---

### 4. Create Data

**Endpoint:** `POST /data/:table/`

**Description:** Create new data records for a specific table.

**Required Roles:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`

**Headers:**
- `Authorization: Bearer <jwt_token>`
- `Content-Type: application/json`

**Path Parameters:**
| Parameter | Type   | Description              |
|-----------|--------|--------------------------|
| `table`   | string | The data table name        |

**Body:**
- `object`: The data to create (varies by table type)

**Response:**
- `201 Created`: Created data record

---

### 5. Find All Data

**Endpoint:** `GET /data/:table/`

**Description:** Retrieve all data records for a specific table with optional query parameters.

**Required Roles:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`, `SHIGURE_USER`

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Path Parameters:**
| Parameter | Type   | Description              |
|-----------|--------|--------------------------|
| `table`   | string | The data table name        |

**Query Parameters:**
- Various query parameters depending on the table type (flattened query format)

**Supported Tables:**
- `driver`: Driver data
- `file`: File data
- `bios`: BIOS data
- `ec`: EC data
- `app`: Application data
- `appfile`: Application file data

**Response:**
- `200 OK`: Array of data records

---

### 6. Find One Data

**Endpoint:** `GET /data/:table/:id`

**Description:** Retrieve a specific data record by ID for a given table.

**Required Roles:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`, `SHIGURE_USER`

**Headers:**
- `Authorization: Bearer <jwt_token>`

**Path Parameters:**
| Parameter | Type   | Description              |
|-----------|--------|--------------------------|
| `table`   | string | The data table name        |
| `id`      | string | The target data ID         |

**Query Parameters:**
- Various query parameters depending on the table type

**Supported Tables & Special Routes:**
- `driver`: Find driver by ID
- `driverprj`: Find driver by project
- `bios`: Find BIOS by ID
- `biosprj`: Find BIOS by project
- `ec`: Find EC by ID
- `ecprj`: Find EC by project
- `app`: Find app by ID
- `appprj`: Find app by project

**Response:**
- `200 OK`: Data record object

---

### 7. Update Data

**Endpoint:** `PATCH /data/:table/:id`

**Description:** Update existing data records for a specific table and ID.

**Required Roles:** `SHIGURE_MASTER`, `SHIGURE_MANAGER`

**Headers:**
- `Authorization: Bearer <jwt_token>`
- `Content-Type: application/json`

**Path Parameters:**
| Parameter | Type   | Description              |
|-----------|--------|--------------------------|
| `table`   | string | The data table name        |
| `id`      | string | The target data ID         |

**Body:**
- `object`: The updated data fields

**Response:**
- `200 OK`: `{ "message": "Data updated successfully" }`

---

## Data Response Structures

### 1. Driver Data Response (`DRIVER`, `DRIVERPRJ`)

Returns detailed driver information including file metadata, controller details, and vendor information.

**JSON Response Columns:**

| Column Name     | Type          | Description                                                  |
|-----------------|---------------|--------------------------------------------------------------|
| `id`            | string        | Unique identifier for the driver                             |
| `projectId`     | string        | Project identifier                                           |
| `categoryId`    | string        | Category identifier                                          |
| `controllerId`  | string        | Controller identifier                                        |
| `vender`        | string        | Vendor name                                                  |
| `osId`          | string        | Operating system identifier                                  |
| `fileId`        | string        | Associated file identifier                                   |
| `driverVer`     | string        | Driver version                                               |
| `driverDate`    | Date/null     | Driver release date                                          |
| `appVer`        | string        | Application version                                          |
| `appDate`       | Date/null     | Application release date                                     |
| `appName`       | string        | Application name                                             |
| `packageName`   | string        | Package name                                                 |
| `packagePath`   | string        | Package file path                                            |
| `packageSha256` | string        | Package SHA-256 hash                                         |
| `packageMd5`    | string        | Package MD5 hash                                             |
| `infName`       | string        | INF file name                                                |
| `infPath`       | string        | INF file path                                                |
| `infSha256`     | string        | INF file SHA-256 hash                                        |
| `infMd5`        | string        | INF file MD5 hash                                            |
| `sbomName`      | string        | SBOM file name                                               |
| `sbomPath`      | string        | SBOM file path                                               |
| `sbomSha256`    | string        | SBOM file SHA-256 hash                                       |
| `sbomMd5`       | string        | SBOM file MD5 hash                                           |
| `noteName`      | string        | Note file name                                               |
| `notePath`      | string        | Note file path                                               |
| `releaseId`     | string        | Release identifier                                           |
| `releaseDate`   | Date/null     | Release date                                                 |
| `command`       | string        | Command string                                               |
| `whqlId`        | string        | WHQL identifier                                              |
| `hwId`          | string        | Hardware identifier                                          |
| `wuId`          | string        | Windows Update identifier                                    |
| `note`          | string        | Additional notes                                             |
| `ecr`           | string        | Engineering Change Request (ECR) number                      |
| `statusId`      | string        | Status identifier                                            |
| `visible`       | boolean       | Visibility flag                                              |
| `level`         | number        | Access level required                                        |
| `dataStatus`    | number        | Data status (0: INITIAL, 1: READY, 2: UPLOADED, 3: CALLBACKED, 4: BYPASS) |
| `errStatus`     | number        | Error status (0: NOPROBLEM, or other error codes)            |
| `creator`       | string        | Creator name (alias if available, otherwise name)            |
| `creatorId`     | string        | Creator user identifier                                      |
| `new`           | boolean       | New flag                                                     |

---

### 2. EC Data Response (`EC`, `ECPRJ`)

Returns Embedded Controller (EC) information including EC files, SMT files, and SBOM details.

**JSON Response Columns:**

| Column Name     | Type          | Description                                                  |
|-----------------|---------------|--------------------------------------------------------------|
| `id`            | string        | Unique identifier for the EC                                 |
| `categoryId`    | string        | Category identifier                                          |
| `projectId`     | string        | Project identifier                                           |
| `stageId`       | string        | Stage identifier                                             |
| `releaseId`     | string        | Release identifier                                           |
| `version`       | string        | EC version                                                   |
| `note`          | string        | Additional notes                                             |
| `releaseDate`   | Date/null     | Release date                                                 |
| `ecr`           | string        | Engineering Change Request (ECR) number                      |
| `visible`       | boolean       | Visibility flag                                              |
| `level`         | number        | Access level required                                        |
| `ecName`        | string        | EC file name                                                 |
| `ecPath`        | string        | EC file path                                                 |
| `ecSha256`      | string        | EC file SHA-256 hash                                         |
| `ecMd5`         | string        | EC file MD5 hash                                             |
| `smtName`       | string        | SMT file name                                                |
| `smtPath`       | string        | SMT file path                                                |
| `smtSha256`     | string        | SMT file SHA-256 hash                                        |
| `smtMd5`        | string        | SMT file MD5 hash                                            |
| `sbomName`      | string        | SBOM file name                                               |
| `sbomPath`      | string        | SBOM file path                                               |
| `sbomSha256`    | string        | SBOM file SHA-256 hash                                       |
| `sbomMd5`       | string        | SBOM file MD5 hash                                           |
| `smtCheck`      | string        | SMT check string                                             |
| `noteName`      | string        | Note file name                                               |
| `notePath`      | string        | Note file path                                               |
| `command`       | string        | Command string                                               |
| `dataStatus`    | number        | Data status (0: INITIAL, 1: READY, 2: UPLOADED, 3: CALLBACKED, 4: BYPASS) |
| `errStatus`     | number        | Error status (0: NOPROBLEM, or other error codes)            |
| `creator`       | string        | Creator name (alias if available, otherwise name)            |
| `creatorId`     | string        | Creator user identifier                                      |

---

### 3. BIOS Data Response (`BIOS`, `BIOSPRJ`)

Returns BIOS information including BIOS files, SMT files, and SBOM details.

**JSON Response Columns:**

| Column Name     | Type          | Description                                                  |
|-----------------|---------------|--------------------------------------------------------------|
| `id`            | string        | Unique identifier for the BIOS                               |
| `categoryId`    | string        | Category identifier                                          |
| `projectId`     | string        | Project identifier                                           |
| `stageId`       | string        | Stage identifier                                             |
| `releaseId`     | string        | Release identifier                                           |
| `whqlId`        | string/null   | WHQL identifier                                              |
| `wuId`          | string/null   | Windows Update identifier                                    |
| `version`       | string        | BIOS version                                                 |
| `note`          | string        | Additional notes                                             |
| `releaseDate`   | Date/null     | Release date                                                 |
| `ecr`           | string        | Engineering Change Request (ECR) number                      |
| `visible`       | boolean       | Visibility flag                                              |
| `level`         | number        | Access level required                                        |
| `biosName`      | string        | BIOS file name                                               |
| `biosPath`      | string        | BIOS file path                                               |
| `biosSha256`    | string        | BIOS file SHA-256 hash                                       |
| `biosMd5`       | string        | BIOS file MD5 hash                                           |
| `smtName`       | string        | SMT file name                                                |
| `smtPath`       | string        | SMT file path                                                |
| `smtSha256`     | string        | SMT file SHA-256 hash                                        |
| `smtMd5`        | string        | SMT file MD5 hash                                            |
| `sbomName`      | string        | SBOM file name                                               |
| `sbomPath`      | string        | SBOM file path                                               |
| `sbomSha256`    | string        | SBOM file SHA-256 hash                                       |
| `sbomMd5`       | string        | SBOM file MD5 hash                                           |
| `smtCheck`      | string        | SMT check string                                             |
| `noteName`      | string        | Note file name                                               |
| `notePath`      | string        | Note file path                                               |
| `command`       | string        | Command string                                               |
| `dataStatus`    | number        | Data status (0: INITIAL, 1: READY, 2: UPLOADED, 3: CALLBACKED, 4: BYPASS) |
| `errStatus`     | number        | Error status (0: NOPROBLEM, or other error codes)            |
| `creator`       | string        | Creator name (alias if available, otherwise name)            |
| `creatorId`     | string        | Creator user identifier                                      |

---

### 4. Application Data Response (`APP`, `APPPRJ`)

Returns application information including application files, package details, and associated metadata.

**JSON Response Columns:**

| Column Name     | Type          | Description                                                  |
|-----------------|---------------|--------------------------------------------------------------|
| `id`            | string        | Unique identifier for the application                        |
| `projectId`     | string        | Project identifier                                           |
| `categoryId`    | string        | Category identifier                                          |
| `controllerId`  | string        | Controller identifier                                        |
| `vender`        | string        | Vendor name                                                  |
| `osId`          | string        | Operating system identifier                                  |
| `fileId`        | string        | Associated file identifier                                   |
| `driverVer`     | string        | Driver version                                               |
| `driverDate`    | Date/null     | Driver release date                                          |
| `appVer`        | string        | Application version                                          |
| `appDate`       | Date/null     | Application release date                                     |
| `appName`       | string        | Application name                                             |
| `packageName`   | string        | Package name                                                 |
| `packagePath`   | string        | Package file path                                            |
| `packageSha256` | string        | Package SHA-256 hash                                         |
| `packageMd5`    | string        | Package MD5 hash                                             |
| `infName`       | string        | INF file name                                                |
| `infPath`       | string        | INF file path                                                |
| `infSha256`     | string        | INF file SHA-256 hash                                        |
| `infMd5`        | string        | INF file MD5 hash                                            |
| `sbomName`      | string        | SBOM file name                                               |
| `sbomPath`      | string        | SBOM file path                                               |
| `sbomSha256`    | string        | SBOM file SHA-256 hash                                       |
| `sbomMd5`       | string        | SBOM file MD5 hash                                           |
| `noteName`      | string        | Note file name                                               |
| `notePath`      | string        | Note file path                                               |
| `releaseId`     | string        | Release identifier                                           |
| `releaseDate`   | Date/null     | Release date                                                 |
| `command`       | string        | Command string                                               |
| `whqlId`        | string        | WHQL identifier                                              |
| `hwId`          | string        | Hardware identifier                                          |
| `wuId`          | string        | Windows Update identifier                                    |
| `note`          | string        | Additional notes                                             |
| `ecr`           | string        | Engineering Change Request (ECR) number                      |
| `statusId`      | string        | Status identifier                                            |
| `visible`       | boolean       | Visibility flag                                              |
| `level`         | number        | Access level required                                        |
| `dataStatus`    | number        | Data status (0: INITIAL, 1: READY, 2: UPLOADED, 3: CALLBACKED, 4: BYPASS) |
| `errStatus`     | number        | Error status (0: NOPROBLEM, or other error codes)            |
| `creator`       | string        | Creator name (alias if available, otherwise name)            |
| `creatorId`     | string        | Creator user identifier                                      |
| `new`           | boolean       | New flag                                                     |

---

## Status Codes Explanation

### Data Status (`dataStatus`)

| Value | Status      | Description                          |
|-------|-------------|--------------------------------------|
| 0     | INITIAL     | Initial state                        |
| 1     | READY       | Ready state                          |
| 2     | UPLOADED    | Uploaded state                       |
| 3     | CALLBACKED  | Callbacked state                     |
| 4     | BYPASS      | Bypass state                         |

### Error Status (`errStatus`)

| Value | Status        | Description                          |
|-------|---------------|--------------------------------------|
| 0     | NOPROBLEM     | No problems                          |
| 11    | NOTREADY      | Not ready                            |
| 12    | ECR_WRONG     | ECR wrong                            |
| 13    | FILE_ERR      | File error                           |
| 14    | ECR_WORKING   | ECR working                          |
| 15    | SC_WRONG      | SC wrong                             |
| 21    | UPLOAD_ERR    | Upload error                         |
| 22    | CALLBACK_ERR  | Callback error                       |
| 23    | UPDATE_ERR    | Update error                         |

---

## Data Table Types

| Table Type   | Description                    |
|--------------|--------------------------------|
| `DRIVER`     | Driver data                    |
| `DRIVERPRJ`  | Driver project data            |
| `FILE`       | General file data              |
| `CATEGORY`   | Category data                  |
| `CONTROLLER` | Controller data                |
| `VENDER`     | Vender data                    |
| `WU`         | Windows Update data            |
| `WHQL`       | WHQL data                      |
| `OS`         | OS data                        |
| `BIOS`       | BIOS data                      |
| `BIOSPRJ`    | BIOS project data              |
| `BCATEGORY`  | BIOS category data             |
| `EC`         | EC (Embedded Controller) data  |
| `ECPRJ`      | EC project data                |
| `ECATEGORY`  | EC category data               |
| `APP`        | Application data               |
| `APPFILE`    | Application file data          |
| `APPPRJ`     | Application project data       |
| `ACATEGORY`  | Application category data      |
| `PROJECT`    | Project data                   |
| `STAGE`      | Project stage data             |
| `USERDATA`   | User data                      |
