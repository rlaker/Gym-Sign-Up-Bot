import win32com.client
import datetime
import argparse
from settings import USERNAME, PASSWORD

def make_bat(u, pw, day, court):
    txt = "\"C:\\Users\\Ronan\\Anaconda3\\envs\\browser\\python.exe\" \"C:\\Users\\Ronan\\Booking Bot\\Gym-Sign-Up-Bot\\main.py\" \"{}\" \"{}\" \"{}\" {}".format(u, pw, day, court)
    with open(f'book_{day}_{court}.bat', 'w') as output:
        output.write(txt)

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('u', type=str, help='Username')
    parser.add_argument('pw', type=str, help='Password')
    parser.add_argument('day',  type=str, help='Date in YYYY-MM-DD format')
    parser.add_argument('court',  type=int, help='Select the court you want')
    
    args = parser.parse_args()

    cur_time = datetime.datetime.now()
        
    #decide how to handle the day argument too
    
    #this script will run on Saturday at 23:58
    #so the booking day is 29 days in the future  
    booking_day = cur_time + datetime.timedelta(days = 29)
    #check that booking day matches the user inputted day
    if booking_day.strftime("%Y-%m-%d") != args.day:
        raise Exception("Booking and inputted day do not match")
    
    start_time = cur_time.replace(hour = 23, minute = 58)

    scheduler(args.u, args.pw, args.day, args.court, start_time)