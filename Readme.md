# TaskLine – Task Manager CLI

A full-stack task management app with **shared workspaces** and **per-user task isolation**.

* **Backend:** FastAPI + SQLModel (hosted on Render)
* **Database:** PostgreSQL on Neon (persistent cloud DB)
* **Frontend:** Terminal-based CLI (Python, requests)


## **Features**

* User registration & login with **JWT authentication**
* Secure password hashing (argon2)
* CRUD tasks per user, with **priority** and **status**
* Shared workspace management with members & task tracking
* Persistent login per device
* Terminal-friendly CLI with **scrolling, highlighting, and workspace views**

## Results
<img width="480" height="476" alt="image" src="https://github.com/user-attachments/assets/987f7aa6-9a0a-4c4b-a24d-20eef0fa7c71" />
<img width="712" height="481" alt="image" src="https://github.com/user-attachments/assets/540bf624-ebd5-46fc-97a9-abafb57f9a87" />
<img width="856" height="445" alt="image" src="https://github.com/user-attachments/assets/97740d73-1993-4f26-a0e9-8c8eac84876a" />
<img width="893" height="683" alt="image" src="https://github.com/user-attachments/assets/15a8afdd-c7a6-4057-aabc-916d3d45e4bd" />


## **Installation – CLI**
### **From release**:
Download the taskline binary and place it in ~/.local/bin. Make it executable. 
             
    chmod +x  ~/.local/bin/taskline
    taskline
      
### **1. Clone the repo**

```bash
git clone git@github.com:MemoritiK/TaskLine.git
cd TaskLine
```

### **2. Install CLI**

```bash
chmod +x taskline.sh
./taskline.sh install
```

* Adds `taskline` command to `~/.local/bin` (ensure it’s in your `PATH`)
* Automatically creates a virtual environment and installs `requests`

### **3. Run the CLI**

```bash
taskline
```

* First run: register a user
* Then login to manage tasks and workspaces

### **4. Uninstall CLI**

```bash
./taskline.sh uninstall
```

## **Backend**

* Hosted on **Render** → accessible via cloud
* API endpoints (base URL provided by Render)
* Handles authentication, tasks, and workspace management

> Users only need the CLI; no need to run backend locally.


## **Database**

* **Neon PostgreSQL** for persistent, multi-user task storage
* CLI and backend connect to the same DB, ensuring shared data across all users


## **CLI Commands Overview**

* `taskline` → launches terminal UI
* Full task CRUD, workspace management, session persistence
* Highlights high-priority tasks, dims completed ones
* Pagination & scrolling supported


## **Tech Stack**

* **Backend:** FastAPI, SQLModel, PostgreSQL (Neon)
* **Frontend:** Python CLI with curses
* **Authentication:** JWT, Argon2 password hashing
