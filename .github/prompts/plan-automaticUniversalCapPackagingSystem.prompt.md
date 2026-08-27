## Plan: Automatic Universal Cap Packaging System

**TL;DR:** Build a FastAPI-based automatic universal cap packaging system with user authentication, project management, weekly build scheduling, and file retention (keep 3 latest files per project). The system will provide an HTML management page for project selection and build status display, with authentication and data acquisition following the Shigure API patterns. A SQL database will be used to manage project schedules, build status, and file retention tracking locally on the server. Project management functions will be restricted to managers only, with manager names configured in the `.env` file. The project will use `uv` for Python project handling and dependency management, and SQLite (built-in) with SQLAlchemy ORM (installed via `uv add sqlalchemy`) for the database. The server will also function as an MCP (Model Context Protocol) server with tools for packaging, listing, and downloading universal cap packages.

**Steps**

**Phase 1: Project Setup & FastAPI Foundation**
1. Initialize FastAPI project structure using `uv` for project handling and dependency management (create project with `uv init`, add dependencies with `uv add fastapi uvicorn jinja2 sqlalchemy aiosqlite python-dotenv apscheduler python-jose[cryptography] passlib[bcrypt]`)
2. Set up FastAPI with HTML template rendering (Jinja2) and static file serving
3. Configure JWT authentication middleware following the Shigure Api-auth.md patterns (JwtGuard, roles: SHIGURE_MASTER, SHIGURE_MANAGER, SHIGURE_USER)
4. Set up SQLite database (built into Python, no separate database server required) with SQLAlchemy ORM (installed via `uv add sqlalchemy`) and `aiosqlite` for async support
5. Create configuration management to load manager names from `.env` file using `python-dotenv` (installed via `uv add python-dotenv`)

**Phase 2: Authentication System**
6. Implement login endpoint (`POST /auth`) accepting username/password and returning JWT token with user info (id, name, role, level)
7. Implement current user endpoint (`GET /auth`) requiring JWT authentication and role validation
8. Create HTML login page with authentication form

**Phase 3: Data Acquisition from Shigure Data Center**
9. Implement Shigure API client for data acquisition following Shigure Api-data.md patterns
10. Create endpoints for data retrieval:
    - `GET /data/:table/` for finding all data records
    - `GET /data/:table/:id` for specific data records
    - Supported tables: driver, driverprj, bios, biosprj, ec, ecprj, app, appprj, file, appfile
11. Implement file upload/download endpoints:
    - `POST /data/upload/:id` for single file upload
    - `POST /data/uploads/:id` for multiple files upload
    - `POST /data/download/:table/:id` for data download

**Phase 4: Project Management & Weekly Build Scheduling (Local Database - Managers Only)**
12. Implement database models for project scheduling and build status using SQLAlchemy:
    - `Project` model with fields: id, name, description, status, created_at, updated_at
    - `BuildSchedule` model with fields: id, project_id, schedule_type (weekly), next_run_time, is_active, created_at, updated_at
    - `BuildHistory` model with fields: id, project_id, build_status (success/failed/in_progress), started_at, completed_at, output_file_path, ids_used
13. Implement project management endpoints with manager-only access control:
    - `GET /projects/` - list all available projects (managers only)
    - `POST /projects/:id/schedule` - schedule a project for weekly build (saves to database) (managers only)
    - `POST /projects/:id/build` - manually trigger a build for a project (managers only)
    - `GET /projects/:id/status` - get build status for a project (reads from database) (managers only)
14. Implement weekly build scheduler using `APScheduler` (installed via `uv add apscheduler`) that reads scheduled projects from the database
15. Implement build logic to execute `package_script.py` (universal cap build script) with two input parameters: 1) project name, 2) token for shigure (obtained from user login). Before executing `package_script.py`, run `check_script` first and send the IDs from the last build (retrieved from the database) to the `check_script` to verify if it is ok to build. When weekly build starts or manual build is triggered, put this script in a thread and run it. Ensure no parallel threads are allowed; run the build scripts one by one (sequential execution). The output of `package_script.py` will be a JSON which contains: 1. path to packaged file, 2. the IDs used for packaging. Update build status in the database based on the script execution result, and save the path to packaged file and the IDs used for packaging to the database.

**Phase 5: File Retention & Storage Management (Local Database)**
16. Implement database model for file tracking using SQLAlchemy:
    - `BuildFile` model with fields: id, project_id, file_name, file_path, build_history_id, created_at
17. Implement file retention logic: keep exactly 3 latest files per project, delete older files
18. Create storage management service to track and cleanup old build files, updating database records
19. Implement endpoint to retrieve available packaged files: `GET /projects/:id/files/` (reads from database)

**Phase 6: HTML Management Page**
20. Create HTML management page with:
    - Login functionality (redirect to login if not authenticated)
    - Project selection interface for weekly build scheduling (managers only)
    - Manual build trigger button/interface to start the packing process of a project manually (managers only)
    - Build status display for each project (reads from database)
    - Download links for packaged universal cap files (reads from database)
21. Implement HTML pages routing in FastAPI:
    - `/login` - login page
    - `/dashboard` - project management and build status page (managers only)
    - `/download/:project_id/:file_id` - file download endpoint

**Phase 7: MCP Server Integration**
22. Configure the FastAPI server to also function as an MCP (Model Context Protocol) server
23. Implement MCP tools for universal cap package management:
    - `package`: Tool to trigger the packaging process of a universal cap package for a specific project (requires project name and shigure token)
    - `list`: Tool to list available packaged universal cap files for a project (reads from database)
    - `download`: Tool to download a specific packaged universal cap file by project_id and file_id

**Relevant files**
- `./app/core/package.py` - universal cap build script, takes two input parameters: 1) project name, 2) token for shigure (obtained from user login). Output is a JSON containing path to packaged file and the IDs used for packaging.
- `./app/core/check.py` - verification script, takes a string array of IDs as input, and outputs true or false to verify if it is ok to build.
- `./app/service/mail_service.py` - includes the sending mail function for error logging and notifications
- `./.github/reference/Shigure Api-auth.md` - authentication API reference for JWT implementation and role-based access control
- `./.github/reference/Shigure Api-data.md` - data API reference for Shigure data center integration (upload, download, CRUD operations)
- `.env` - environment configuration file containing manager names

**Database Schema**
- **Projects Table**: id, name, description, status, created_at, updated_at
- **BuildSchedules Table**: id, project_id, schedule_type, next_run_time, is_active, created_at, updated_at
- **BuildHistories Table**: id, project_id, build_status, started_at, completed_at, output_file_path, ids_used
- **BuildFiles Table**: id, project_id, file_name, file_path, build_history_id, created_at

**Verification**
1. Initialize project using `uv init` and verify dependency installation with `uv add` commands
2. Start FastAPI server and verify `/docs` endpoint shows all API routes
3. Test login endpoint with valid/invalid credentials and verify JWT token generation
4. Test authentication middleware by accessing protected endpoints with and without valid JWT
5. Verify HTML pages render correctly at `/login` and `/dashboard`
6. Test project scheduling endpoint and verify weekly scheduler is active and saves to database
7. Test manual build trigger endpoint (`POST /projects/:id/build`) and verify it starts the build process
8. Verify build status endpoint reads from database correctly
9. Verify file retention logic keeps exactly 3 latest files per project and deletes older ones, updating database records
10. Test universal cap file packaging and download functionality
11. Verify that project management endpoints and dashboard are only accessible by managers listed in the `.env` file

**Decisions**
- **Project Handling**: Use `uv` for Python project handling, dependency management, and virtual environment creation (replacing standard pip/virtualenv)
- **Authentication**: Follow Shigure Api-auth.md patterns with JWT tokens and role-based access (SHIGURE_MASTER, SHIGURE_MANAGER, SHIGURE_USER)
- **Manager Access Control**: Project management functions are restricted to managers only, with manager names configured in the `.env` file
- **Data Acquisition**: Follow Shigure Api-data.md patterns for data retrieval, upload, and download operations
- **Scheduling**: Use APScheduler for weekly build scheduling, with schedule data stored in local SQL database
- **Manual Build Trigger**: Provide HTML interface for managers to manually start the packing process of a project via `POST /projects/:id/build` endpoint
- **Build Execution**: Before executing `package.py`, run `check.py` first and send the IDs from the last build (retrieved from the database) to the `check.py` to verify if it is ok to build. If verification passes, execute `package.py` with two input parameters: 1) project name, 2) token for shigure (obtained from user login) in a thread when weekly build starts or manual build is triggered. No parallel threads are allowed; build scripts must run one by one (sequential execution). The output of `package.py` is a JSON containing: 1. path to packaged file, 2. the IDs used for packaging. These two are saved to the database.
- **Build Status**: Store and retrieve build status from local SQL database (BuildHistories table), including the path to packaged file and the IDs used for packaging.
- **File Retention**: Keep exactly 3 latest build files per project, automatically delete older files, with file tracking in local SQL database (BuildFiles table)
- **HTML Templates**: Use Jinja2 for server-side HTML rendering with FastAPI
- **Database**: Use SQLite (built into Python, no separate server required) with SQLAlchemy ORM (installed via `uv add sqlalchemy`) and `aiosqlite` for async support
- **MCP Server**: The server will also function as an MCP (Model Context Protocol) server with tools for packaging, listing, and downloading universal cap packages

**Further Considerations**
1. **Universal Cap Data Structure**: The specific data fields needed for universal cap packaging will be discussed later. Should the system be designed with a modular data acquisition approach to easily accommodate different data schemas?
Ans: the output of `package.py` is a JSON which contains: 1. path to packaged file, 2. the IDs used for packaging.
2. **Build File Naming Convention**: What naming convention should be used for the packaged universal cap files to easily identify build date and version?
Ans: Project name + build date.
3. **Check Script Verification**: Before packaging, the system should run `check.py` with the IDs from the last build (retrieved from the database) to verify if it is ok to build. The `check.py` takes a string array of IDs as input and outputs true or false.
4. **Error Handling & Notifications**: Yes, the system should include error logging and notifications (email/webhook) when build failures occur or when file retention cleanup happens. The system should use `./app/service/mail_service.py`, which includes the sending mail function, for email notifications.
5. **Manager Configuration**: Yes, the `.env` file should be structured with manager names in a specific format like `MANAGERS=user1,user2,user3` for clarity and ease of parsing.
6. **uv Commands**: Project initialization will use `uv init <project-name>`, dependency installation will use `uv add <package>`, and running the server will use `uv run fastapi dev main.py` or `uv run python main.py`.
7. **MCP Tools Integration**: The MCP server tools (package, list, download) should integrate with the existing database and file retention logic, ensuring consistent state management across both HTML UI and MCP tool interfaces.
