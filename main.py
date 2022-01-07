import time as sleepytime
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
import argparse
from settings import DRIVER_PATH
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import io
from webdriver_manager.firefox import GeckoDriverManager
from datetime import datetime
from selenium.common import exceptions as exc

with io.open("url.txt", encoding="utf-8") as f:
    BASE_URL = f.read()

def get_driver_path():
    if(DRIVER_PATH):
        return DRIVER_PATH
    else:
        # raise Exception("You need to set the chrome driver path in the DRIVER_PATH environment variable.")
        with io.open("driver_path.txt", encoding="utf-8") as f:
            return f.read()

def get_day_url(day):
    return BASE_URL + '#' + f'?date={day}&role=member'

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
    
    
def main(u, pw, day, court, wait_midnight = False):
    t = datetime.datetime.now()
    print(f'[STARTING] Signing up for court {court} on {day}')
    print(get_driver_path())
    # s=Service(get_driver_path())
    
    browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    #browser = webdriver.Firefox(executable_path=get_driver_path()) #webdriver.Chrome(service=s)
    
    browser.get(BASE_URL)
    
    
    login(u, pw, browser)
    
    print(get_day_url)
    
    if wait_midnight:
        #wait until midnight
        time  = datetime.now()
        counter = 0
        print(f"Started waiting at {time}")
        while time < datetime(time.year, time.month, time.day+1,0,0):#start of the next day
            if counter == 10:
                print(time)
                counter = 0
                
            time  = datetime.now()
            sleepytime.sleep(0.5)
            counter += 1
    
    #wait an extra 0.5 seconds before loading the page again
    time.sleep(0.5)
    
    #wait for the slot to become bookable
    
    try:
        book_slot(court, day, '07:00', browser, hour = True)
        #make sure you comment this line out when testing
        #confirm(browser)
    except:
        #browser.close()
        raise Exception("failed to book")
    
    try:
        book_slot(court, day, '08:00', browser, hour = False)
        #make sure you comment this line out when testing
        #confirm(browser)
    except:
        browser.close()
        raise Exception("failed to book")
    
    

    print(f"[SUCCESS] Signed up for court {court}")
    
    sleepytime.sleep(2)

    browser.close()
    
if __name__ == "__main__":
    print('doing a thing')
    parser = argparse.ArgumentParser()

    parser.add_argument('u', type=str, help='Username')
    parser.add_argument('pw', type=str, help='Password')
    parser.add_argument('day',  type=str, help='Select the day you want to book')
    parser.add_argument('court',  type=int, help='Select the court you want')

    args = parser.parse_args()

    main(args.u, args.pw, args.day, args.court)



