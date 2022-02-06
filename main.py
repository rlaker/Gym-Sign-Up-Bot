import argparse
import time as sleepytime
from datetime import datetime, timedelta

import yagmail
from selenium import webdriver
from selenium.common import exceptions as exc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from settings import DRIVER_PATH, TENNIS_EMAIL_SENDER, URL


def get_day_url(day):
    """returns the url for the right day"""
    return URL + "#" + f"?date={day}&role=member"


def login(u, pw, browser):
    """Login the user

    Parameters
    ----------
    u : str
        username
    pw : str
        password
    browser : browser object
    """
    # click the login button
    WebDriverWait(browser, 10).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "ajax-wrapper"))
    )
    WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Login"))
    ).click()

    sleepytime.sleep(0.2)
    # find the username and password box
    username = WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.NAME, "EmailAddress"))
    )
    username_str = u
    # send the username str
    username.send_keys(username_str)

    # find the password element
    password = browser.find_element(By.NAME, "Password")
    password_str = pw
    password.send_keys(password_str)

    # click the sign in button
    browser.find_element(By.ID, "signin-btn").click()


def convert_time_to_id(time="10:00"):
    """Converts a time string to the number format used in the website

    Parameters
    ----------
    time : str, optional
        Time to convert, by default '10:00'

    Returns
    -------
    int
        Minutes since midnight, which is what the page uses
    """
    return int(time[:2]) * 60 + int(time[3:])


def is_slot_bookable(slot):
    """Checks if slot if bookable by looking at the text in the slot elements

    Parameters
    ----------
    slot : slot object
        slot object after finding through selenium

    Returns
    -------
    str

    """
    try:
        # if the slot is bookable then
        slot.find_element(By.XPATH, ".//a[@class='book-interval not-booked']")
        return "available"
    except exc.NoSuchElementException as e:
        # print('It is not available')
        pass

    try:
        # search for the unavailable class
        slot.find_element(By.CLASS_NAME, "unavailable")
        return "unavailable"

    except exc.NoSuchElementException as e:
        # print("It is not unavailable")
        pass

    try:
        slot.find_element(By.XPATH, ".//a[@class='edit-booking']")
        return "booked"

    except exc.NoSuchElementException as e:
        pass

    raise Exception("It is none of these options")


class AlreadyBooked(Exception):
    """Class for case when court is already booked"""

    def __init__(self, max_refresh):
        self.max_refresh = max_refresh

    def __str__(self):
        return f"Still not available after refreshing {self.max_refresh} times"


class Unavailable(Exception):
    """Class for case when court is already booked"""

    def __init__(self, max_refresh):
        self.max_refresh = max_refresh

    def __str__(self):
        return f"Already booked!\nGo and check: {self.url}"


def book_slot(court, day, time, browser, hour=False):
    """Finds the right court and books it.

    Parameters
    ----------
    court : int
        Court number
    day : str
        Date to book in YY-MM-DD format
    time : str
        time to book in HH-MM
    browser : browser object
        browser object
    hour : bool, optional
        If True will book court for an hour, by default False

    """

    # Go to the correct date url
    browser.get(get_day_url(day))
    sleepytime.sleep(2)

    # find the court to book
    court_obj = WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//div[@data-resource-name='Court {court}']")
        )
    )
    # this finds the div of the right slot
    slot = court_obj.find_element(
        By.XPATH, f".//div[@data-system-start-time='{convert_time_to_id(time)}']"
    )

    # if slot is unavailable then it is not ready to book yet, so try max_refresh times.
    refresh_count = 0
    max_refresh = 20
    while is_slot_bookable(slot) == "unavailable" and refresh_count < max_refresh:
        print("Unavailable, refreshing the page after 5 secs")
        sleepytime.sleep(5)

        # reload the page and try again
        browser.refresh()
        refresh_count += 1

        # have to refind the slots
        court_obj = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//div[@data-resource-name='Court {court}']")
            )
        )
        # this finds the div of the right slot
        slot = court_obj.find_element(
            By.XPATH, f".//div[@data-system-start-time='{convert_time_to_id(time)}']"
        )

    answer = is_slot_bookable(slot)
    if answer == "unavailable":
        raise Unavailable(max_refresh)

    elif answer == "booked":
        # this slot is already booked
        raise AlreadyBooked(get_day_url(day))

    WebDriverWait(browser, 5).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "ajax-wrapper"))
    )
    # need to scroll so that the cookie policy does not go above the slot
    browser.execute_script('arguments[0].scrollIntoView({block: "center"});', slot)

    WebDriverWait(browser, 5).until(EC.element_to_be_clickable(slot)).click()

    # click on the slot which brings up a pop-up
    popup = WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.XPATH, "//form[@action='Book']"))
    )

    # if hour is true we need to choose from dropdown menu
    if hour:
        # this bit selects the full hour
        select = (
            WebDriverWait(browser, 5)
            .until(
                EC.element_to_be_clickable(
                    popup.find_element(
                        By.XPATH, ".//span[@class='select2-selection__arrow']"
                    )
                )
            )
            .click()
        )

        select = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable(
                popup.find_element(By.XPATH, ".//span[@class='selection']")
            )
        )

        select_dropdown = WebDriverWait(browser, 5).until(
            EC.element_to_be_clickable(
                select.find_element(By.XPATH, ".//span[@aria-expanded='true']")
            )
        )
        select_dropdown.send_keys(Keys.DOWN)

        select_dropdown.send_keys(Keys.RETURN)

    # press the continue button
    WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable(popup.find_element(By.ID, "submit-booking"))
    ).click()


def click_confirm(browser):
    """Clicks the confirm button"""
    confirm_buttom = WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.ID, "confirm"))
    )
    browser.execute_script(
        'arguments[0].scrollIntoView({block: "center"});', confirm_buttom
    )
    WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.ID, "confirm"))
    ).click()


def get_default_target_date():
    """Gets the target date for the default.

    Returns
    -------
    str
        Target date to book

    Raises
    ------
    Exception
        If script not started on a Saturday
    Exception
        If target day is not a Sunday
    """

    weekday_dic = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday",
    }

    # the script will start running on saturday night, so the weekday should be 6
    # but our target date is in 29 days time - and should be a sunday
    script_start_date = datetime.now()
    if script_start_date.isocalendar().weekday == 6:
        # 29 because the script started on saturday, but want to book when turns midnight and becomes sunday
        target_date = script_start_date + timedelta(days=29)
        wait_midnight = True
        # check this is a sunday
        print(
            f"Target date is {target_date}, on a {weekday_dic[target_date.isocalendar().weekday]}"
        )

    elif script_start_date.isocalendar().weekday == 7:
        print("Script started on the Sunday, maybe you loaded a bit late")
        print("Will try and book in 28 days still")
        target_date = script_start_date + timedelta(days=28)
        wait_midnight = False
        # check this is a sunday
        if target_date.isocalendar().weekday == 7:
            print(
                f"Target date is {target_date} on a {weekday_dic[target_date.isocalendar().weekday]}"
            )
        else:
            raise Exception(
                "Started script on Sunday and target date did not come out as a Sunday"
            )
    else:
        raise Exception(
            f"You have started this script on {weekday_dic[script_start_date.isocalendar().weekday]}. \n You have to specify the date instead."
        )

    # need to return as a string
    return target_date.strftime("%Y-%m-%d"), wait_midnight


def send_email(u, day, court, time, condition="success"):
    """Sends email to confirm the booking by this bot

    Just send if a success for now
    """
    # follow Yagmail documentation to save password to keyring
    yag = yagmail.SMTP(TENNIS_EMAIL_SENDER)

    if condition == "success":
        contents = [
            f"Python has booked Court {court} at {time} on {day}",
            f'<a href="{get_day_url(day)}">Check for yourself!</a>',
        ]
        outcome = "SUCCESS"
    else:
        raise Exception("Condition doesn't match what I expected")

    yag.send(u, f"[{outcome}] Court {court} at {time} on {day}", contents)
    yag.send(
        "ronan.laker@gmail.com",
        f"[{outcome}] Court {court} at {time} on {day}",
        contents,
    )
    print("[SENT] Sent the confirmation email")


def main(u, pw, day, court, time, confirm, wait_midnight=False):
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
    # if no values set by the user then use the default values
    if day is None:
        default = True
        # get the target booking date
        day, wait_midnight = get_default_target_date()

    # keep this condition separate in case you want default day but new court number
    if court is None:
        court = 3

    if time is None:
        time = "10:00"

    print(f"[STARTING] Signing up for court {court} at {time} on {day}")

    # start the firefox browser
    # takes a  few seconds
    browser = webdriver.Firefox(service=Service(DRIVER_PATH))
    browser.get(URL)

    # login to the page before midnight, so we are ready to go
    login(u, pw, browser)

    # waits until midnight has passed
    if wait_midnight:
        now = datetime.now()
        tomorrow = datetime(now.year, now.month, now.day + 1)

        # wait until midnight
        time = datetime.now()
        counter = 0
        print(f"Started waiting at {time}")
        while time < tomorrow:  # start of the next day
            if counter == 10:
                print(f"Time is {time}, waiting until {tomorrow}")
                counter = 0

            time = datetime.now()
            sleepytime.sleep(0.5)
            counter += 1

    # wait an extra 0.5 seconds before loading the page again
    sleepytime.sleep(0.5)

    # tries to book the first court
    try:

        book_slot(court, day, time, browser, hour=True)

        # make sure you comment this line out when testing
        # confirm the booking, without pressing it wont book
        if confirm:
            click_confirm(browser)
        # INDENT if you don't want to send emails when testing
        if TENNIS_EMAIL_SENDER is not None:
            send_email(u, day, court, time)
    except:
        browser.close()
        raise Exception("failed to book")

    # by default we want to book another half an hour from 11:00 to 11:30
    if default:
        try:
            book_slot(court, day, "11:00", browser, hour=False)

            # make sure you comment this line out when testing
            # confirm the booking, without pressing it wont book
            if confirm:
                click_confirm(browser)
        except:
            browser.close()
            raise Exception("failed to book")

    print(f"[SUCCESS] Signed up for court {court}")

    print("[INFO] Closing Browser in 10 seconds")
    sleepytime.sleep(10)
    browser.close()


def str2bool(v):
    # taken from https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("u", type=str, help="Username")
    parser.add_argument("pw", type=str, help="Password")
    parser.add_argument("--day", "-d", type=str, help="Select the day you want to book")
    parser.add_argument("--court", "-c", type=int, help="Select the court you want")
    parser.add_argument(
        "--time",
        "-t",
        type=str,
        help="Select the time",
    )
    parser.add_argument(
        "--confirm",
        type=str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Whether to click confirm",
    )

    args = parser.parse_args()

    main(args.u, args.pw, args.day, args.court, args.time, args.confirm)
