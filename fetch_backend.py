import os
import json
from datetime import date
import requests
import getpass

SESSION_FILE = ".task_manager_session"

BASE_URL_USERS = "http://127.0.0.1:8000/users"
BASE_URL_TASKS = "http://127.0.0.1:8000/tasks"

def save_session(token, user):
    """Save JWT and user info locally"""
    data = {"token": token, "user": user}
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)

def load_session():
    """Load logged-in user and JWT from local file"""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def register_user():
    """Register new user (does NOT log in)"""
    print('\n',"=== Register ===")
    name = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    r = requests.post(f"{BASE_URL_USERS}/register/", json={"name": name, "password": password})
    if r.status_code == 200:
        print("User registered successfully!")
    else:
        print("Error:", r.json())
    input("Press Enter to continue...")

def login_user():
    """Login user and store JWT locally"""
    print('\n',"=== Login ===")
    name = input("Username: ").strip()    
    password = getpass.getpass("Password: ")
    r = requests.post(f"{BASE_URL_USERS}/login/", json={"name": name, "password": password})
    if r.status_code == 200:
        token_data = r.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        # Verify token to get user info
        v = requests.get(f"{BASE_URL_USERS}/verify", headers=headers)
        if v.status_code == 200:
            user = v.json()
            save_session(token_data['access_token'], user)
            print(f"Logged in as {user['name']}")
            input("Press Enter to continue...")
            return {"token": token_data['access_token'], "user": user}
        else:
            print("Error verifying user:", v.json())
            input("Press Enter to continue...")
    else:
        print("Login failed:", r.json())
        input("Press Enter to continue...")
    return None

def login_or_register():
    """Menu until user logs in"""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Welcome to Task Manager CLI!\n")
        print("1. Login")
        print("2. Register")
        print("q. Quit")
        choice = input("Choose option: ").strip()
        if choice == "1":
            user = login_user()
            if user:
                return user
        elif choice == "2":
            register_user()
        elif choice.lower() == "q":
            exit()

def fetch_tasks(user_id, token):
    """Get tasks for user, unfinished first"""
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL_TASKS}/{user_id}", headers=headers)
    tasks = r.json()
    tasks.sort(key=lambda x: x.get("status") == "completed")
    return tasks

def add_task(name, priority, user_id, token):
    today = date.today()
    date_created = today.strftime("%b %-d")
    data = {"name": name, "priority": priority, "date": date_created, "status": "new", "user_id": user_id}
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{BASE_URL_TASKS}/{user_id}", json=data, headers=headers)

def update_task(task_id, name, priority, user_id, token, status=None):
    today = date.today()
    date_created = today.strftime("%b %-d")
    data = {"name": name, "priority": priority, "date": date_created, "user_id": user_id}
    if status:
        data["status"] = status
    headers = {"Authorization": f"Bearer {token}"}
    requests.put(f"{BASE_URL_TASKS}/{user_id}/{task_id}", json=data, headers=headers)

def delete_task(task_id, user_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    requests.delete(f"{BASE_URL_TASKS}/{user_id}/{task_id}", headers=headers)

def toggle_task_status(task, user_id, token):
    new_status = "completed" if task["status"] == "new" else "new"
    update_task(task["id"], task["name"], task["priority"], user_id, token, status=new_status)
