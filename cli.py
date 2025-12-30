import curses
import os
from fetch_backend import*
LOGOUT = "LOGOUT"
QUIT = "QUIT"

def get_input(stdscr, prompt):
    curses.echo()
    height, width = stdscr.getmaxyx()
    stdscr.move(height-2,0)
    stdscr.clrtoeol()
    stdscr.addstr(height-2,0,prompt)
    stdscr.refresh()
    user_input = stdscr.getstr(height-2,len(prompt)).decode()
    curses.noecho()
    return user_input.strip()


def task_management_ui(stdscr,session,token,user,id,mode:str):
    cursor = 0
    offset = 0
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # high priority

    while True:
        stdscr.clear()
        if mode == "personal":
          tasks = fetch_personal_tasks(id, token)
        else:
            tasks = fetch_shared_tasks(id,token)
        num_tasks = len(tasks)
        height, width = stdscr.getmaxyx()
        display_height = height - 6

        # Title and instructions
        title = f"Task Line - {user['name']}"
        if mode != "personal":
            title+=f"\n Workspace: {mode}"
        x = (width - len(title)) // 2
        stdscr.addstr(0, x, title, curses.A_BOLD | curses.A_UNDERLINE)
        stdscr.addstr(2, 0, " Instructions: a=Add, u=Update, Space=Toggle Complete, d=Delete, q=Quit, r=reload")

        # Scrolling
        if cursor < offset:
            offset = cursor
        elif cursor >= offset + display_height:
            offset = cursor - display_height + 1
        header_y = 4

        if mode != "personal":
            header = f"{'':3} {'Name':<40} {'Priority':<10} {'Date':<8}  {'Created By'}"
        else:
            header = f"{'':3} {'Name':<40} {'Priority':<10} {'Date':<8}"

        stdscr.addstr(header_y, 0, header[:width-1], curses.A_BOLD)

        # Display tasks
        for idx in range(offset, min(offset + display_height, num_tasks)):
            task = tasks[idx]
            checkbox = "[x]" if task["status"] == "completed" else "[ ]"
            
            if mode != "personal":
                line = f"{checkbox} {task['name']:<40} {task['priority']:<10} {task['date']:<8}  [{task.get('created_by', '')}]"
            else:
                line = f"{checkbox} {task['name']:<40} {task['priority']:<10} {task['date']:<8}"
            
            y = 5 + idx - offset
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
        elif k == ord("r"):
            continue
        elif k == ord("q"):
            break
        elif k == ord("d") and tasks:
            if mode == "personal":
               delete_personal_task(tasks[cursor]["id"], id, token)
            else:
               delete_shared_task(tasks[cursor]["id"], id, token)
            if cursor >= len(tasks) - 1 and cursor > 0:
                cursor -= 1
        elif k == ord(" "):  # toggle completed
            if tasks:
                if mode == "personal":
                    toggle_personal_task(tasks[cursor], id, token)
                else:
                    toggle_shared_task(tasks[cursor], id, token)
        elif k == ord("a") and user:
            name = get_input(stdscr, "Enter task name: ")
            while True:
                prio_input = get_input(stdscr, "Priority? [n]ormal/[h]igh: ").upper()
                if prio_input in ["N","H"]:
                    priority = "Normal" if prio_input=="N" else "High"
                    break
            if mode == "personal":
                add_personal_task(name, priority, id, token)
            else:
                add_shared_task(name, priority, id, token)
                
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
            if mode == "personal":
                update_personal_task(task["id"], name, priority, id, token)
            else:
                update_shared_task(task["id"], name, priority, id, token)
    

# Personal Task Menu  
def personal_task_menu(stdscr, session):
    token = session["token"]
    user = session["user"]
    user_id = user["id"]
    task_management_ui(stdscr,session,token,user,user_id,"personal")

# ------------------ Shared Workspace Menu ------------------ #
def shared_workspace_menu(stdscr, session):
    token = session["token"]
    user = session['user']
    username = user["name"]
    curses.curs_set(0)
    
    while True:
        workspaces = list(fetch_workspaces(token).values() or [])
        num_ws = len(workspaces)
        cursor = 0
        offset = 0
        height, width = stdscr.getmaxyx()
        display_height = height - 6

        while True:
            # Fetch workspaces every iteration to refresh
            workspaces_dict = fetch_workspaces(token) or {}   # fetch dict from backend
            workspaces = list(workspaces_dict.values())   # convert to list
            num_ws = len(workspaces)
            stdscr.clear()
            stdscr.addstr(0, (width-25)//2, "Shared Workspaces", curses.A_BOLD | curses.A_UNDERLINE)
            stdscr.addstr(2, 0, "Instructions: Enter=Open, a=Add, d=Delete, m=Add/Remove Members , q=Back, r=Reload")

            # Ensure cursor is valid
            if num_ws == 0:
                cursor = 0
            elif cursor >= num_ws:
                cursor = num_ws - 1

            # Scrolling
            if cursor < offset:
                offset = cursor
            elif cursor >= offset + display_height:
                offset = cursor - display_height + 1

            # Table header
            header_y = 3
            stdscr.addstr(header_y + 1, 0,
                f"{'Name':<20} {'Owner':<15} {'Role':<10} {'Members'}",
                curses.A_BOLD)            
            start_y = header_y + 3
            
            # Table rows
            for idx in range(offset, min(offset + display_height, num_ws)):
                ws = workspaces[idx]
                
                role = "Owner" if ws["owner"] == username else "Member"
                members = ", ".join(ws["members"]) if ws["members"] else "—"
                
                line = (
                    f"{ws['name']:<20} "
                    f"{ws['owner']:<15} "
                    f"{role:<10} "
                    f"{members}"
                )
                
                attr = curses.A_REVERSE if idx == cursor else curses.A_NORMAL
                stdscr.addstr(start_y + idx - offset, 0, line[:width - 1], attr)


            stdscr.refresh()
            k = stdscr.getch()

            if k == curses.KEY_UP and cursor > 0:
                cursor -= 1
            elif k == curses.KEY_DOWN and cursor < num_ws - 1:
                cursor += 1
            elif k == ord("q"):
                return  # back to main menu
            elif k in [10, 13] and num_ws > 0:  # Enter: open workspace tasks
                ws = workspaces[cursor]
                task_management_ui(stdscr,session,token,user,ws["workspace_id"],ws["name"])
            elif k == ord("r"):
                continue
            elif k == ord("a"):  # create workspace
                name = get_input(stdscr, "Workspace name: ")
                wid = create_workspace(name, username, token)
                if wid:
                    while True:
                        add_more = get_input(stdscr, "Add a member? (y/n): ").lower()
                        if add_more != "y":
                            break
                        member_name = get_input(stdscr, "Enter member username: ")
                        add_workspace_member(wid, member_name, token)

            elif k == ord("d") and num_ws > 0:  # delete workspace
                ws = workspaces[cursor]
                msg = delete_workspace(ws["workspace_id"], token)
                height, width = stdscr.getmaxyx()
                stdscr.addstr(
                    height-2,
                    2,
                    msg[:width-4],
                    curses.A_BOLD | curses.A_REVERSE
                )
                stdscr.refresh()
                curses.napms(1500) 
            elif k == ord("m") and num_ws > 0:  # manage members
                ws = workspaces[cursor]
            
                while True:
                    stdscr.addstr(height-2, 0, "Options: a=Add Member, r=Remove Member, b=Back")
                    stdscr.refresh()
            
                    action = stdscr.getch()
            
                    if action == ord("b"):  # back to workspace menu
                        break
            
                    elif action == ord("a") and ws["owner"] == username:
                        # Add member form at bottom
                        while True:
                            stdscr.addstr(height-1, 0, "Enter member username to add (blank to stop): ")
                            stdscr.clrtoeol()
                            stdscr.refresh()
                            member_name = get_input(stdscr, "")
                            if not member_name:
                                break
                            msg = add_workspace_member(ws["workspace_id"], member_name, token)
                            height, width = stdscr.getmaxyx()
                            stdscr.addstr(
                                height-3,
                                2,
                                msg[:width-4],
                                curses.A_BOLD | curses.A_REVERSE
                            )
                            stdscr.refresh()
                            curses.napms(1000) 
                            continue  
            
                    elif action == ord("r"):
                        # Remove member form at bottom
                        while True:
                            stdscr.addstr(height-1, 0, "Enter member username to remove (blank to stop): ")
                            stdscr.clrtoeol()
                            stdscr.refresh()
                            member_name = get_input(stdscr, "")
                            if not member_name:
                                break
                            if member_name in ws["members"]:
                                msg = remove_workspace_member(ws["workspace_id"], member_name, token)
                                height, width = stdscr.getmaxyx()
                                stdscr.addstr(
                                    height-3,
                                    2,
                                    msg[:width-4],
                                    curses.A_BOLD | curses.A_REVERSE
                                )
                                stdscr.refresh()
                                curses.napms(1000)
                                continue


def run_main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        
        session = load_session()
        if not session:
            session = login_or_register()
            if not session:
                return  # user chose quit at login
        
        result = curses.wrapper(lambda stdscr: main_curses(stdscr, session))
 
        if result == LOGOUT:
            continue   # restart app → login screen again

        if result == QUIT:
            break      # exit program cleanly

    
def main_curses(stdscr, session):
    while True:
        stdscr.clear()
        curses.curs_set(0)        
        h, w = stdscr.getmaxyx()
    
        PAD_Y = 2
        PAD_X = 2
    
        height = h - PAD_Y * 2
        width = w - PAD_X * 2
    
        win = curses.newwin(height, width, PAD_Y, PAD_X)
        win.keypad(True)
            
        title = f"Task Line CLI - {session['user']['name']}"
        win.addstr(0,(width-len(title))//2,title,curses.A_BOLD|curses.A_UNDERLINE)
        win.addstr(2, 0, "Options:")
        win.addstr(3, 2, "1. Personal Tasks")
        win.addstr(4, 2, "2. Shared Workspaces")
        win.addstr(5, 2, "l. Logout")
        win.addstr(6, 2, "q. Quit")
        win.refresh()
        k = win.getch()
        if k==ord("1"):
            personal_task_menu(win, session)
        elif k==ord("2"):
            shared_workspace_menu(win, session)
        elif k==ord("l"):  # Explicit logout
             clear_session()
             return LOGOUT
        elif k==ord("q"):  # Exit program but keep JWT valid
             return QUIT

    
if __name__=="__main__":
    run_main()

