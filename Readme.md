# Task Manager API

A simple **Task Manager REST API** built with **FastAPI** and **SQLModel (SQLite)**.

* Create, read, update, and delete tasks
* Each task has:

  * `name` (string)
  * `priority` (`Normal` or `High`)
  * `date` (string, automatically generated as `Jan 2` style)
  * `status` (`new` or `completed`)
* Fully compatible with CLI or any frontend


## **Features**

* RESTful API endpoints for task management
* Automatic creation date
* Simple SQLite database for storage
* Dependency-injected database sessions
* Supports pagination (`offset` + `limit`)

## **Requirements**

* Python 3.10+
* FastAPI, SQLModel, Uvicorn

```bash
pip install fastapi sqlmodel uvicorn
```

## **API Endpoints**

| Method   | Endpoint      | Description                                    |
| -------- | ------------- | ---------------------------------------------- |
| `GET`    | `/tasks/`     | List all tasks (supports `offset` and `limit`) |
| `POST`   | `/tasks/`     | Create a new task                              |
| `PUT`    | `/tasks/{id}` | Update an existing task                        |
| `DELETE` | `/tasks/{id}` | Delete a task                                  |

### **Example JSON**

**Create task:**

```json
{
  "name": "Buy milk",
  "priority": "Normal",
  "date": "Jan 2"
}
```

**Response for GET `/tasks/`:**

```json
[
  {
    "id": 1,
    "name": "Buy milk",
    "priority": "Normal",
    "date": "Jan 2"
  },
  {
    "id": 2,
    "name": "Study math",
    "priority": "High",
    "date": "Jan 3"
  }
]
```

## **Running the API**

```bash
uvicorn main:app --reload
```

* The API will be available at: `http://127.0.0.1:8000`
* Interactive API docs available at:

  * Swagger: `http://127.0.0.1:8000/docs`
  * ReDoc: `http://127.0.0.1:8000/redoc`


## **Future Improvements**

* Add **authentication / authorization**
* Add **search / filter** endpoints
* Add **completed/done status** for tasks