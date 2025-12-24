import os
import json
from datetime import date
import requests
import getpass

SESSION_FILE = ".task_manager_session"

BASE_URL_USERS = "http://127.0.0.1:8000/users"
BASE_URL_PERSONAL_TASKS = "http://127.0.0.1:8000/personaltasks"
BASE_URL_SHARED_TASKS = "http://127.0.0.1:8000/sharedtasks"
BASE_URL_WORKSPACES = "http://127.0.0.1:8000/workspaces"

#  Session Management 
def save_session(token, user):
    data = {"token": token, "user": user}
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# Auth 
def register_user():
    print("\n=== Register ===")
    name = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    r = requests.post(f"{BASE_URL_USERS}/register/", json={"name": name, "password": password})
    print("Success!" if r.status_code == 200 else "Error: "+str(r.json()))
    input("Press Enter to continue...")

def login_user():
    print("\n=== Login ===")
    name = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    r = requests.post(f"{BASE_URL_USERS}/login/", json={"name": name, "password": password})
    if r.status_code == 200:
        token_data = r.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        v = requests.get(f"{BASE_URL_USERS}/verify", headers=headers)
        if v.status_code == 200:
            user = v.json()
            save_session(token_data['access_token'], user)
            print(f"Logged in as {user['name']}")
            input("Press Enter to continue...")
            return {"token": token_data['access_token'], "user": user}
        else:
            print("Error verifying user:", v.json())
    else:
        print("Login failed:", r.json())
    input("Press Enter to continue...")
    return None

def login_or_register():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\033[0GWelcome to Task Line CLI!\n")  # \033[0G moves cursor to column 0
        print("\033[0G1. Login")
        print("\033[0G2. Register")
        print("\033[0Gq. Quit")

        choice = input("Choose option: ").strip()
        if choice == "1":
            user = login_user()
            if user: return user
        elif choice == "2":
            register_user()
        elif choice.lower() == "q":
            exit()

# Personal Task APIs 
def fetch_personal_tasks(user_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL_PERSONAL_TASKS}/{user_id}", headers=headers)
    tasks = r.json()
    tasks.sort(key=lambda x: x.get("status")=="completed")
    return tasks

def add_personal_task(name, priority, user_id, token):
    today = date.today()
    data = {"name": name, "priority": priority, "date": today.strftime("%b %-d"), "status": "new", "user_id": user_id}
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{BASE_URL_PERSONAL_TASKS}/{user_id}", json=data, headers=headers)

def update_personal_task(task_id, name, priority, user_id, token, status=None):
    today = date.today()
    data = {"name": name, "priority": priority, "date": today.strftime("%b %-d"), "user_id": user_id}
    if status: data["status"] = status
    headers = {"Authorization": f"Bearer {token}"}
    requests.put(f"{BASE_URL_PERSONAL_TASKS}/{user_id}/{task_id}", json=data, headers=headers)

def delete_personal_task(task_id, user_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    requests.delete(f"{BASE_URL_PERSONAL_TASKS}/{user_id}/{task_id}", headers=headers)

def toggle_personal_task(task, user_id, token):
    new_status = "completed" if task["status"]=="new" else "new"
    update_personal_task(task["id"], task["name"], task["priority"], user_id, token, status=new_status)

# Shared Workspace & Tasks APIs  
def fetch_workspaces(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{BASE_URL_WORKSPACES}/", headers=headers)
        if r.status_code == 200:
            data = r.json()
            if not data:
                return {}  # Return empty list if no workspaces
            return data
        else:
            return {}  # treat errors as empty
    except Exception:
        return {}


def create_workspace(name, owner, token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": name, "owner": owner}
    r = requests.post("http://127.0.0.1:8000/workspaces/", json=data, headers=headers)
    try:
        wid = r.json()  # this returns workspace_id according to your backend
        return wid
    except Exception as e:
        print("Error creating workspace:", r.text)
        return None


def delete_workspace(workspace_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.delete(f"{BASE_URL_WORKSPACES}/{workspace_id}", headers=headers)
    if r.status_code == 403:
        return "Permission denied (not owner)"
    return "Deleted!"
    
def add_workspace_member(workspace_id, member_name, token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"workspace_id": workspace_id, "member": member_name}
    r = requests.post(f"http://127.0.0.1:8000/workspaces/{workspace_id}/members", json=data, headers=headers)
    if r.status_code == 403:
        return "Permission denied (not owner)"
    if r.status_code == 404:
        return "User not found!"
    return "Added successfully!"

def remove_workspace_member(workspace_id, member_name, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.delete(f"{BASE_URL_WORKSPACES}/{workspace_id}/members/{member_name}", headers=headers)
    if r.status_code == 403:
        return "Permission denied (not owner)"
    if r.status_code == 404:
        return "User not found!"
    return "Removed successfully!"
     
def fetch_shared_tasks(workspace_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL_SHARED_TASKS}/{workspace_id}", headers=headers)
    tasks = r.json()
    tasks.sort(key=lambda x: x.get("status")=="completed")
    return tasks

def add_shared_task(name, priority, workspace_id, token):
    today = date.today()
    data = {"name": name, "priority": priority, "date": today.strftime("%b %-d"), "status":"new", "workspace_id": workspace_id}
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{BASE_URL_SHARED_TASKS}/{workspace_id}", json=data, headers=headers)

def update_shared_task(task_id, name, priority, workspace_id, token, status=None):
    today = date.today()
    data = {"name": name, "priority": priority, "date": today.strftime("%b %-d")}
    if status: data["status"] = status
    headers = {"Authorization": f"Bearer {token}"}
    requests.put(f"{BASE_URL_SHARED_TASKS}/{workspace_id}/{task_id}", json=data, headers=headers)

def delete_shared_task(task_id, workspace_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    requests.delete(f"{BASE_URL_SHARED_TASKS}/{workspace_id}/{task_id}", headers=headers)

def toggle_shared_task(task, workspace_id, token):
    new_status = "completed" if task["status"]=="new" else "new"
    update_shared_task(task["id"], task["name"], task["priority"], workspace_id, token, status=new_status)
