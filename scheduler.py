import win32com.client
import datetime
import argparse
from settings import USERNAME, PASSWORD

"""
def scheduler(u, pw, day, court, st):
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    root_folder = scheduler.GetFolder('\\')
    print(f"root folder is {root_folder}")
    new_task = scheduler.NewTask(0)
    
    task_name = f"Tennis booker {day}"
    print(f"[CREATING] Scheduling task named {task_name}")

    TASK_TRIGGER_TIME = 1
    trigger = new_task.Triggers.Create(TASK_TRIGGER_TIME)
    trigger.StartBoundary = st.isoformat()

    TASK_ACTION_EXEC = 0
    action = new_task.Actions.Create(TASK_ACTION_EXEC)
    action.ID = 'DO NOTHING'
    
    # path of python interpreter
    action.Path = "C:\\Users\\Ronan\\Anaconda3\\envs\\browser\\python.exe" 
    
    
    action.Arguments = "C:\\Users\\Ronan\\Booking Bot\\Gym-Sign-Up-Bot\\main.py {} {} {} {}".format(u, pw, day, court) # args for python interpreter

    new_task.RegistrationInfo.Description = "Tennis Booking"
    new_task.Settings.Enabled = True
    new_task.Settings.StopIfGoingOnBatteries = False
    new_task.Settings.DisallowStartIfOnBatteries = False
    new_task.Settings.WakeToRun = True

    TASK_CREATE_OR_UPDATE = 6
    TASK_LOGON_NONE = 0
    root_folder.RegisterTaskDefinition(
        task_name,
        new_task,
        TASK_CREATE_OR_UPDATE,
        '',  # No user
        '',  # No password
        TASK_LOGON_NONE)

    print(f'[SUCCESS] Created gym sign up for {day}')
    
    return new_task

"""
def make_bat(u, pw, day, court, time):
    if day == None:
        txt = f"\"C:\\Users\\Ronan\\Anaconda3\\envs\\browser\\python.exe\" \"C:\\Users\\Ronan\\Booking Bot\\Projects\\Gym-Sign-Up-Bot\\main.py\" \"{u}\" \"{pw}\""
    if court == None:
        court  = 3
    else:
        txt = f"\"C:\\Users\\Ronan\\Anaconda3\\envs\\browser\\python.exe\" \"C:\\Users\\Ronan\\Booking Bot\\Gym-Sign-Up-Bot\\main.py\" \"{u}\" \"{pw}\" \"-d\" \"{day}\" \"-c\" \"{court}\" \"-t\" \"{time}\""
    
    with open(f'book.bat', 'w') as output:
        output.write(txt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('u', type=str, help='Username')
    parser.add_argument('pw', type=str, help='Password')
    parser.add_argument('--day', '-d',  type=str, help='Select the day you want to book')
    parser.add_argument('--court', '-c',  type=int, help='Select the court you want')
    parser.add_argument('--time', '-t',  type=str, help='Select the time', )

    args = parser.parse_args()
    
    make_bat(args.u, args.pw, args.day, args.court, args.time)