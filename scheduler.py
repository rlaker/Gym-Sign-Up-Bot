import win32com.client
import datetime
import argparse
from settings import USERNAME, PASSWORD

def get_username():
    if(USERNAME):
        return USERNAME
    else:
        raise Exception("You need to set your username in the USERNAME environment variable.")

def get_password():
    if(PASSWORD):
        return PASSWORD
    else:
        raise Exception("You need to set your password in the PASSWORD environment variable.")

def scheduler(u, pw, day, court, st):
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()
    root_folder = scheduler.GetFolder('\\')
    new_task = scheduler.NewTask(0)
    
    task_name = "Gym sign up {}".format(st.strftime('%m-%d'))
    print("[CREATING] Scheduling task named '{}'".format(task_name))

    TASK_TRIGGER_TIME = 1
    trigger = new_task.Triggers.Create(TASK_TRIGGER_TIME)
    trigger.StartBoundary = st.isoformat()

    TASK_ACTION_EXEC = 0
    action = new_task.Actions.Create(TASK_ACTION_EXEC)
    action.ID = 'DO NOTHING'
    action.Path = "C:\\Users\\Tjmon\\anaconda3\\python.exe" # path of python interpreter
    action.Arguments = "C:\\Users\\Tjmon\\OneDrive\\Desktop\\Gym-Sign-Up-Bot-Project\\main.py {} {} {} {}".format(u, pw, floor, t) # args for python interpreter

    new_task.RegistrationInfo.Description = "Gym sign up"
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

    print('[SUCCESS] Created gym sign up for {} on {}'.format(t, st.strftime('%m/%d')))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('u', type=str, help='Username')
    parser.add_argument('pw', type=str, help='Password')
    parser.add_argument('day',  type=str, help='Date in YYYY-MM-DD format')
    parser.add_argument('court',  type=int, help='Select the court you want')
    
    args = parser.parse_args()

    cur_time = datetime.datetime.now()
    
    #this needs to be changed to midnight on the sunday
    #decide if you want to want to just run this schedular on the day
    start_task_hour = int(args.t[:2]) - 6
    start_task_minutes = int(args.t[3:])
    
    #decide how to handle the day argument too
    #check it is 4 weeks ahead
    if(not args.d):
        # If its past the six hours in advance of the gym slot opening, set the date to the next day
        if(start_task_hour < cur_time.hour):
            start_time = datetime.datetime(cur_time.year, cur_time.month, cur_time.day+1, start_task_hour, start_task_minutes)
        elif(start_task_hour == cur_time.hour and start_task_minutes < cur_time.minute):
            start_time = datetime.datetime(cur_time.year, cur_time.month, cur_time.day+1, start_task_hour, start_task_minutes) 
        else: 
            start_time = datetime.datetime(cur_time.year, cur_time.month, cur_time.day, start_task_hour, start_task_minutes)
    else:
        start_time = datetime.datetime(int(args.d[6:]), int(args.d[:2]), int(args.d[3:5]), start_task_hour, start_task_minutes)

    scheduler(args.u, args.pw, args.day, args.court, start_time)