import curses
import requests
from datetime import date

BASE_URL = "http://127.0.0.1:8000"  # FastAPI backend URL

def fetch_tasks():
    r = requests.get(f"{BASE_URL}/tasks/")
    return r.json()

def add_task(name, priority):
    today = date.today()
    date_created = today.strftime("%b %-d")  # e.g., 'Jan 2'
    data = {"name": name, "priority": priority, "date": date_created}
    requests.post(f"{BASE_URL}/tasks/", json=data)

def update_task(task_id, name, priority):
    today = date.today()
    date_created = today.strftime("%b %-d")
    data = {"name": name, "priority": priority, "date": date_created}
    requests.put(f"{BASE_URL}/tasks/{task_id}", json=data)

def delete_task(task_id):
    requests.delete(f"{BASE_URL}/tasks/{task_id}")

def get_input(stdscr, prompt):
    """Prompt for input at the bottom line"""
    curses.echo()
    height, width = stdscr.getmaxyx()
    stdscr.move(height - 2, 0)
    stdscr.clrtoeol()
    stdscr.addstr(height - 2, 0, prompt)
    stdscr.refresh()
    user_input = stdscr.getstr(height - 2, len(prompt)).decode()
    curses.noecho()
    return user_input.strip()

def main(stdscr):
    curses.curs_set(0)
    k = 0
    cursor = 0
    offset = 0  # for scrolling

    while True:
        stdscr.clear()
        tasks = fetch_tasks()
        num_tasks = len(tasks)
        height, width = stdscr.getmaxyx()
        display_height = height - 6  # title + instructions + bottom prompt

        # Title
        stdscr.addstr(0, 0, "Task Manager", curses.A_BOLD | curses.A_UNDERLINE)
        # Instructions
        stdscr.addstr(2, 0, "Instructions: a=Add, u=Update, Space=Delete, q=Quit")

        # Adjust scrolling offset
        if cursor < offset:
            offset = cursor
        elif cursor >= offset + display_height:
            offset = cursor - display_height + 1

        # Display tasks
        for idx in range(offset, min(offset + display_height, num_tasks)):
            task = tasks[idx]
            name = task["name"]
            priority = task["priority"]
            date_created = task["date"]
            checkbox = "[ ]"
            line = f"{checkbox} {name:<20} {priority:<6} {date_created:<6}"
            y = 4 + idx - offset
            if idx == cursor:
                stdscr.addstr(y, 0, line[:width - 1], curses.A_REVERSE)
            else:
                stdscr.addstr(y, 0, line[:width - 1])

        stdscr.refresh()
        k = stdscr.getch()

        # Navigation
        if k == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif k == curses.KEY_DOWN and cursor < num_tasks - 1:
            cursor += 1
        elif k == ord("q"):
            break
        elif k == ord(" "):  # delete
            if tasks:
                delete_task(tasks[cursor]["id"])
                if cursor >= len(tasks) - 1 and cursor > 0:
                    cursor -= 1
        elif k == ord("a"):  # add task
            name = get_input(stdscr, "Enter task name: ")
            while True:
                prio_input = get_input(stdscr, "Priority? [n]ormal/[h]igh: ").upper()
                if prio_input in ["N", "H"]:
                    priority = "Normal" if prio_input == "N" else "High"
                    break
            add_task(name, priority)
        elif k == ord("u"):  # update highlighted task
            if tasks:
                task = tasks[cursor]
                name = get_input(stdscr, f"Update name ({task['name']}): ")
                if not name:
                    name = task["name"]
                while True:
                    prio_input = get_input(stdscr, f"Update priority ({task['priority']})? [n]ormal/[h]igh: ").upper()
                    if prio_input in ["N", "H"]:
                        priority = "Normal" if prio_input == "N" else "High"
                        break
                    elif prio_input == "":
                        priority = task["priority"]
                        break
                update_task(task["id"], name, priority)

curses.wrapper(main)
