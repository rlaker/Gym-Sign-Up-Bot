import time as sleepytime
from datetime import datetime, timedelta
import argparse
import io
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from settings import DRIVER_PATH, URL
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common import exceptions as exc
from selenium.webdriver.firefox.service import Service  

def get_driver_path():
    if(DRIVER_PATH):
        return DRIVER_PATH
    else:
        # raise Exception("You need to set the chrome driver path in the DRIVER_PATH environment variable.")
        with io.open("driver_path.txt", encoding="utf-8") as f:
            return f.read()

def get_day_url(day):
    return URL + '#' + f'?date={day}&role=member'

def login(u, pw, browser):
    # sleepytime.sleep(3)
    #sign_in = browser.find_element(By.CLASS_NAME,"sign-in")
    WebDriverWait(browser, 5).until(EC.invisibility_of_element_located((By.CLASS_NAME,"ajax-wrapper")))
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Login"))).click()
    
    sleepytime.sleep(0.2)
    #find the username and password box
    username = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.NAME, "EmailAddress")))
    username_str = u
    username.send_keys(username_str)

    password = browser.find_element(By.NAME, "Password")
    password_str = pw
    password.send_keys(password_str)

    browser.find_element(By.ID, "signin-btn").click()
    
    

def convert_time_to_id(time = '10:00'):
    return int(time[:2])*60 + int(time[3:])
    
    
def is_slot_bookable(slot):
    try:
        #if the slot is bookable then 
        slot.find_element(By.XPATH, ".//a[@class='book-interval not-booked']")
        return 'available'  
    except exc.NoSuchElementException as e:
        # print('It is not available')
        pass
    
    try:
        #search for the unavailable class
        slot.find_element(By.CLASS_NAME, "unavailable")
        return 'unavailable'
    
    except exc.NoSuchElementException as e:
        # print("It is not unavailable")
        pass
    
    try:
        slot.find_element(By.XPATH, ".//a[@class='edit-booking']")
        return 'booked'
    
    except exc.NoSuchElementException as e:
        pass
    
    raise Exception("It is none of these options")

def book_slot(court, day, time, browser, hour = False):
    # print(get_day_url(day))
    # print(convert_time_to_id(time))
    browser.get(get_day_url(day))
    sleepytime.sleep(2)
    # court_obj = browser.find_element(By.XPATH, f"//div[@data-resource-name='Court {court}']")
    
    court_obj = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, f"//div[@data-resource-name='Court {court}']")))
    #this finds the div of the right slot
    slot = court_obj.find_element(By.XPATH, f".//div[@data-system-start-time='{convert_time_to_id(time)}']")
    
    refresh_count = 0
    while is_slot_bookable(slot) == 'unavailable' and refresh_count < 10:
        print("Unavailable, refreshing the page after 5 secs")
        sleepytime.sleep(5)
        
        #reload the page and try again 
        browser.refresh()
        refresh_count += 1
        
        #have to refind the slots
        court_obj = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, f"//div[@data-resource-name='Court {court}']")))
        #this finds the div of the right slot
        slot = court_obj.find_element(By.XPATH, f".//div[@data-system-start-time='{convert_time_to_id(time)}']")
        
    answer = is_slot_bookable(slot)
    print(answer)
    if answer == 'unavailable':
        raise Exception("Still not available after refreshing")
    elif answer == 'booked':
        #this slot is already booked 
        raise Exception(f"Already booked!\n{get_day_url(day)}")
    elif answer == 'available':
        pass
    
    WebDriverWait(browser, 5).until(EC.invisibility_of_element_located((By.CLASS_NAME,"ajax-wrapper")))
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable(slot)).click()
    
    popup = WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.XPATH, "//form[@action='Book']")))
    
    if hour == True:
        #this bit selects the full hour
        select = WebDriverWait(browser, 5).until(EC.element_to_be_clickable(popup.find_element(By.XPATH, ".//span[@class='select2-selection__arrow']"))).click()
        
        select = WebDriverWait(browser, 5).until(EC.element_to_be_clickable(popup.find_element(By.XPATH, ".//span[@class='selection']")))
        
        select_dropdown = WebDriverWait(browser, 5).until(EC.element_to_be_clickable(select.find_element(By.XPATH, ".//span[@aria-expanded='true']")))
        select_dropdown.send_keys(Keys.DOWN)
        
        select_dropdown.send_keys(Keys.RETURN)
        
    
    #press the continue button
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable(popup.find_element(By.ID, "submit-booking"))).click()
    

def confirm(browser):
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.ID, 'confirm'))).click()  
    
def get_default_target_date():
    weekday_dic = {1: 'Monday',
               2: 'Tuesday',
               3: 'Wednesday',
               4: "Thursday",
               5: "Friday",
               6: "Saturday",
               7: "Sunday"}

    # the script will start running on saturday night, so the weekday should be 6
    # but our target date is in 29 days time - and should be a sunday
    script_start_date = datetime.now()
    if script_start_date.isocalendar().weekday == 5:
        #29 because the script started on saturday, but want to book when turns midnight and becomes sunday
        target_date = script_start_date + timedelta(days = 29)
        
        #check this is a sunday
        print(f"Target date is {target_date}, on a {weekday_dic[target_date.isocalendar().weekday]}")
        
    elif script_start_date.isocalendar().weekday == 7:
        print('Script started on the Sunday, maybe you loaded a bit late')
        print("Will try and book in 28 days still")
        target_date = script_start_date + timedelta(days = 28)
        #check this is a sunday
        if target_date.isocalendar().weekday == 7:
            print(f"Target date is {target_date} on a {weekday_dic[target_date.isocalendar().weekday]}")
        else:
            raise Exception("Started script on Sunday and target date did not come out as a Sunday")
    else:
        raise Exception(f'You have started this script on {weekday_dic[script_start_date.isocalendar().weekday]}. \n You have to specify the date instead.')
        
    #need to return as a string
    return target_date.strftime("%Y-%m-%d")
    
def main(u, pw, day, court, time, wait_midnight = False):
    """Main script to book the courts with selenium and Firefox/

    Parameters
    ----------
    u : str
        Username
    pw : str
        Password
    day : str
        Day of court booking in YY-MM-DD format. If None then will use default.
    court : int
        Court number
    time : str
        Start time of the slot in HH:MM format.
    wait_midnight : bool, optional
        If True will wait until midnight before trying to book, by default False
    """
    
    default = False
    #if no values set by the user then use the default values
    if day == None:
        default = True
        #get the target booking date
        day = get_default_target_date()
        wait_midnight = True
    
    # keep this condition separate in case you want default day but new court number
    if court == None:    
        court = 3
        
    if time == None:
        time = '10:00'
    
    print(f'[STARTING] Signing up for court {court} at {time} on {day}')
    
    #start the firefox browser
    # takes a  few seconds
    browser = webdriver.Firefox(service = Service(DRIVER_PATH))
    browser.get(URL)
    
    #login to the page before midnight, so we are ready to go
    login(u, pw, browser)
    
    #waits until midnight has passed
    if wait_midnight:
        now = datetime.now()
        tomorrow = datetime(now.year, now.month, now.day+1)
        
        #wait until midnight
        time  = datetime.now()
        counter = 0
        print(f"Started waiting at {time}")
        while time < tomorrow:#start of the next day
            if counter == 10:
                print(f"Time is {time}, waiting until {tomorrow}")
                counter = 0
                
            time  = datetime.now()
            sleepytime.sleep(0.5)
            counter += 1
    
    #wait an extra 0.5 seconds before loading the page again
    sleepytime.sleep(0.5)
    
    #tries to book the first court
    try:
            
        book_slot(court, day, time, browser, hour = True)
        
        #make sure you comment this line out when testing
        #confirm the booking, without pressing it wont book
        #confirm(browser)
    except:
        browser.close()
        raise Exception("failed to book")
    
    #by default we want to book another half an hour from 11:00 to 11:30
    if default:
        try:
            book_slot(court, day, '11:00', browser, hour = False)
            
            #make sure you comment this line out when testing
            #confirm the booking, without pressing it wont book
            #confirm(browser)
        except:
            browser.close()
            raise Exception("failed to book")
    
    

    print(f"[SUCCESS] Signed up for court {court}")
    
    sleepytime.sleep(1)

    browser.close()
    
if __name__ == "__main__":
    print('doing a thing')
    parser = argparse.ArgumentParser()

    parser.add_argument('u', type=str, help='Username')
    parser.add_argument('pw', type=str, help='Password')
    parser.add_argument('--day', '-d',  type=str, help='Select the day you want to book')
    parser.add_argument('--court', '-c',  type=int, help='Select the court you want')
    parser.add_argument('--time', '-t',  type=str, help='Select the time', )

    args = parser.parse_args()

    main(args.u, args.pw, args.day, args.court, args.time)



