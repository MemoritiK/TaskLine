import curses
from  fetch_backend import *

def get_input(stdscr, prompt):
    curses.echo()
    height, width = stdscr.getmaxyx()
    stdscr.move(height - 2, 0)
    stdscr.clrtoeol()
    stdscr.addstr(height - 2, 0, prompt)
    stdscr.refresh()
    user_input = stdscr.getstr(height - 2, len(prompt)).decode()
    curses.noecho()
    return user_input.strip()

def task_manager_curses(stdscr, session):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # high priority
    k = 0
    cursor = 0
    offset = 0
    token = session["token"]
    user = session["user"]
    user_id = user["id"]

    while True:
        stdscr.clear()
        tasks = fetch_tasks(user_id, token)
        num_tasks = len(tasks)
        height, width = stdscr.getmaxyx()
        display_height = height - 6

        # Title and instructions
        title = f"Task Manager - {user['name']}"
        x = (width - len(title)) // 2
        stdscr.addstr(0, x, title, curses.A_BOLD | curses.A_UNDERLINE)
        stdscr.addstr(2, 0, " Instructions: a=Add, u=Update, Space=Toggle Complete, d=Delete, q=Quit")

        # Scrolling
        if cursor < offset:
            offset = cursor
        elif cursor >= offset + display_height:
            offset = cursor - display_height + 1

        # Display tasks
        for idx in range(offset, min(offset + display_height, num_tasks)):
            task = tasks[idx]
            checkbox = "[x]" if task["status"] == "completed" else "[ ]"
            line = f"{checkbox} {task['name']:<20} {task['priority']:<6} {task['date']:<6}"
            y = 4 + idx - offset
            attr = curses.A_REVERSE if idx == cursor else curses.A_NORMAL
            if task['priority'] == "High":
                attr |= curses.color_pair(1)
            if task["status"] == "completed":
                attr |= curses.A_DIM
            stdscr.addstr(y, 0, line[:width-1], attr)

        stdscr.refresh()
        k = stdscr.getch()

        # Navigation and actions
        if k == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif k == curses.KEY_DOWN and cursor < num_tasks - 1:
            cursor += 1
        elif k == ord("q"):
            break
        elif k == ord("d") and tasks:
            delete_task(tasks[cursor]["id"], user_id, token)
            if cursor >= len(tasks) - 1 and cursor > 0:
                cursor -= 1
        elif k == ord(" "):  # toggle completed
            if tasks:
                toggle_task_status(tasks[cursor], user_id, token)
        elif k == ord("a") and user:
            name = get_input(stdscr, "Enter task name: ")
            while True:
                prio_input = get_input(stdscr, "Priority? [n]ormal/[h]igh: ").upper()
                if prio_input in ["N","H"]:
                    priority = "Normal" if prio_input=="N" else "High"
                    break
            add_task(name, priority, user_id, token)
        elif k == ord("u") and tasks:
            task = tasks[cursor]
            name = get_input(stdscr, f"Update name ({task['name']}): ") or task["name"]
            while True:
                prio_input = get_input(stdscr, f"Update priority ({task['priority']})? [n]ormal/[h]igh: ").upper()
                if prio_input in ["N","H"]:
                    priority = "Normal" if prio_input=="N" else "High"
                    break
                elif prio_input == "":
                    priority = task["priority"]
                    break
            update_task(task["id"], name, priority, user_id, token)

def main():
    os.system('cls' if os.name=='nt' else 'clear')
    session = load_session()
    if not session:
        session = login_or_register()
    curses.wrapper(lambda stdscr: task_manager_curses(stdscr, session))

if __name__=="__main__":
    main()
