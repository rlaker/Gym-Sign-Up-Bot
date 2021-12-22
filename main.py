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
    sleepytime.sleep(3)
    #sign_in = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "sign-in")))
    sign_in = browser.find_element_by_class_name("sign-in")
    sign_in.click()
    
    sleepytime.sleep(0.2)
    #find the username and password box
    username = browser.find_element_by_name("EmailAddress")
    username_str = u
    username.send_keys(username_str)

    password = browser.find_element_by_name("Password")
    password_str = pw
    password.send_keys(password_str)

    browser.find_element_by_id("signin-btn").click()

def convert_time_to_id(time = '10:00'):
    return int(time[:2])*60 + int(time[3:])
    
    
def book_slot(court, day, time, browser, hour = False):
    print(get_day_url(day))
    print(convert_time_to_id(time))
    browser.get(get_day_url(day))
    sleepytime.sleep(2)
    court_obj = browser.find_element(By.XPATH, f"//div[@data-resource-name='Court {court}']")
    slot = court_obj.find_element(By.XPATH, f".//div[@data-system-start-time='{convert_time_to_id(time)}']")
    slot.click()
    popup = browser.find_element(By.XPATH, "//form[@action='Book']")
    
    if hour == True:
        #this bit selects the full hour
        select = popup.find_element(By.XPATH, ".//span[@class='select2-selection__arrow']")
        sleepytime.sleep(1)
        select.click()
        
        select = popup.find_element(By.XPATH, ".//span[@class='selection']")
        select_dropdown = select.find_element(By.XPATH, ".//span[@aria-expanded='true']")
        select_dropdown.send_keys(Keys.DOWN)
        
        select_dropdown.send_keys(Keys.RETURN)
        
    sleepytime.sleep(1)
    #press the continue button
    popup.find_element_by_id("submit-booking").click()
    

def confirm(browser):
    sleepytime.sleep(1)
    browser.find_element_by_id('confirm').click()
    
    
    
def main(u, pw, day, court):
    t = datetime.datetime.now()
    print(f'[STARTING] Signing up for court {court} on {day}')
    print(get_driver_path())
    # s=Service(get_driver_path())
    
    browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    #browser = webdriver.Firefox(executable_path=get_driver_path()) #webdriver.Chrome(service=s)
    
    browser.get(BASE_URL)
    
    
    login(u, pw, browser)
    sleepytime.sleep(2)
    
    
    #have to wait until it actually logs in 
    #element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "carousel")))
    print(get_day_url)
    
    try:
        #think I need to scroll down the page otherwise the cookie notice blocks me
        book_slot(court, day, '07:00', browser, hour = True)
        #confirm(browser)
    except:
        #browser.close()
        raise Exception("failed to book")
    
    sleepytime.sleep(1)
    
    try:
        #think I need to scroll down the page otherwise the cookie notice blocks me
        book_slot(court, day, '08:00', browser, hour = False)
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
    parser.add_argument('court',  type=int, help='Select the court you want')
    parser.add_argument('day',  type=str, help='Select the day you want to book')

    args = parser.parse_args()

    main(args.u, args.pw, args.day, args.court)



