# TaskLine - Task Manager API

A full-stack task management app using Task Manager REST API built with FastAPI and SQLModel (SQLite).

Supports **user authentication**, **JWT-based sessions**, **per-user task isolation**, and **shared workspace management**, with a dedicated terminal-based CLI frontend made from curses.

## **Features**

* [x] User registration and login
* [x] Secure password hashing (argon2)
* [x] Password length enforcement
* [x] JWT authentication with expiration
* [x] Per-user task isolation (tasks are linked to users)
* [x] Task status support (`new` / `completed`)
* [x] Task priority (`Normal` / `High`)
* [x] Automatic date support (`Jan 2` style)
* [x] Pagination (`offset` + `limit`)
* [x] Supports persistent login per device
* [x] **Shared Workspaces**: create, delete, manage members, collaborate 
* [x] Task `created_by` tracking for workspace tasks


## **Tech Stack**

Install dependencies:

```bash
pip install requests fastapi sqlmodel uvicorn passlib[argon2] PyJWT typing
```


## **Core Models**

### **User**

| Field    | Type            |
| -------- | --------------- |
| id       | int (PK)        |
| name     | string (unique) |
| password | hashed string   |

### **Task**

| Field      | Type                    |
| ---------- | ----------------------- |
| id         | int (PK)                |
| name       | string                  |
| priority   | `Normal` / `High`       |
| date       | string (`Jan 2` format) |
| status     | `new` / `completed`     |
| user_id    | int (FK → User)         |
| created_by | string (optional)       |

### **Workspace**

| Field | Type              |
| ----- | ----------------- |
| id    | int (PK)          |
| name  | string            |
| owner | string (username) |

### **Workspace Members**

| Field        | Type                 |
| ------------ | -------------------- |
| id           | int (PK)             |
| workspace_id | int (FK → Workspace) |
| member       | string (username)    |


## **Auth Endpoints**

| Method | Endpoint           | Description                |
| ------ | ------------------ | -------------------------- |
| `POST` | `/users/register/` | Register a new user        |
| `POST` | `/users/login/`    | Login and get JWT          |
| `GET`  | `/users/verify`    | Verify JWT and return user |

---

## **Task Endpoints**

> All task operations are scoped **per user**.

| Method   | Endpoint                     | Description           |
| -------- | ---------------------------- | --------------------- |
| `GET`    | `/tasks/{user_id}`           | List tasks for a user |
| `POST`   | `/tasks/{user_id}`           | Create a new task     |
| `PUT`    | `/tasks/{user_id}/{task_id}` | Update a task         |
| `DELETE` | `/tasks/{user_id}/{task_id}` | Delete a task         |

### **Workspace Task Endpoints**

> Tasks within a workspace track who created them.

| Method   | Endpoint                                     | Description                 |
| -------- | -------------------------------------------- | --------------------------- |
| `GET`    | `/workspaces/{workspace_id}/tasks`           | List tasks in a workspace   |
| `POST`   | `/workspaces/{workspace_id}/tasks`           | Create a new workspace task |
| `PUT`    | `/workspaces/{workspace_id}/tasks/{task_id}` | Update a workspace task     |
| `DELETE` | `/workspaces/{workspace_id}/tasks/{task_id}` | Delete a workspace task     |

---

## **Workspace Endpoints**

| Method   | Endpoint                                           | Description                             |
| -------- | -------------------------------------------------- | --------------------------------------- |
| `GET`    | `/workspaces/`                                     | List all workspaces the user belongs to |
| `POST`   | `/workspaces/`                                     | Create a new workspace                  |
| `DELETE` | `/workspaces/{workspace_id}`                       | Delete a workspace                      |
| `POST`   | `/workspaces/{workspace_id}/members`               | Add a member                            |
| `DELETE` | `/workspaces/{workspace_id}/members/{member_name}` | Remove a member                         |


## **Running the API**

```bash
uvicorn main:app --reload
```
* API base: `http://127.0.0.1:8000`
* Swagger docs: `http://127.0.0.1:8000/docs`
* ReDoc: `http://127.0.0.1:8000/redoc`


## **CLI Frontend**

This API is designed to work with a **curses-based CLI Task Manager** that supports:

* Login / Register
* Local session persistence
* High-priority highlighting
* Completed task dimming
* Scrolling
* Full CRUD task control
* Workspace creation, deletion, and member management
* Viewing and managing tasks per workspace


## **How to Run the App**

### **1. Start the Backend API**

```bash
uvicorn main:app --reload
```

* API will run at `http://127.0.0.1:8000`

### **2. Run the CLI Frontend**

```bash
python cli.py
```

* On first run, choose **Register** to create a user
* Then **Login** to access and manage your tasks and workspaces

### Results
