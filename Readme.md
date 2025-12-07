# Task Manager API

A full-featured **Task Manager REST API** built with **FastAPI** and **SQLModel (SQLite)**.

Supports **user authentication**, **JWT-based sessions**, and **per-user task isolation**, with a dedicated terminal-based CLI frontend.

## **Features**

- [x] User registration and login
- [x] Secure password hashing (bcrypt)
- [x] Password length reinforcement
- [x] JWT authentication with expiration
- [x] Per-user task isolation (tasks are linked to users)
- [x] Task status support (`new` / `completed`)
- [x] Task priority (`Normal` / `High`)
- [x] Automatic date support (`Jan 2` style)
- [x] Pagination (`offset` + `limit`)
- [x] Supports persistent login per device


## **Tech Stack**
Install dependencies:

```bash
pip install fastapi sqlmodel uvicorn passlib[bcrypt] PyJWT typing
```

## **Core Models**

### **User**

| Field    | Type            |
| -------- | --------------- |
| id       | int (PK)        |
| name     | string (unique) |
| password | hashed string   |

### **Task**

| Field    | Type                    |
| -------- | ----------------------- |
| id       | int (PK)                |
| name     | string                  |
| priority | `Normal` / `High`       |
| date     | string (`Jan 2` format) |
| status   | `new` / `completed`     |
| user_id  | int (FK → User)         |


## **Auth Endpoints**

| Method | Endpoint           | Description                |
| ------ | ------------------ | -------------------------- |
| `POST` | `/users/register/` | Register a new user        |
| `POST` | `/users/login/`    | Login and get JWT          |
| `GET`  | `/users/verify`    | Verify JWT and return user |

### **Login Response Example**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## **Task Endpoints**

> All task operations are scoped **per user**.

| Method   | Endpoint                     | Description           |
| -------- | ---------------------------- | --------------------- |
| `GET`    | `/tasks/{user_id}`           | List tasks for a user |
| `POST`   | `/tasks/{user_id}`           | Create a new task     |
| `PUT`    | `/tasks/{user_id}/{task_id}` | Update a task         |
| `DELETE` | `/tasks/{user_id}/{task_id}` | Delete a task         |


## **Example Task JSON**

```json
{
  "name": "Buy milk",
  "priority": "High",
  "date": "Jan 2",
  "status": "new",
  "user_id": 1
}
```


## **Running the API**

```bash
uvicorn main:app --reload
```

* API base: `http://127.0.0.1:8000`
* Swagger docs:
  `http://127.0.0.1:8000/docs`
* ReDoc:
  `http://127.0.0.1:8000/redoc`

## **CLI Frontend**

This API is designed to work with a **curses-based CLI Task Manager** that supports:

* Login / Register
* Local session persistence
* High-priority highlighting
* Completed task dimming
* Scrolling
* Full CRUD task control

