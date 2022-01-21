# Tennis sign up bot

Following this [blog post](https://tmonty.tech/create-an-automated-web-bot-with-selenium-in-python) I adapted it to book tennis courts.

# Instructions

1. Clone (or download) this repo onto your computer.
2. Download the Firefox webdriver, known as [geckodriver](https://github.com/mozilla/geckodriver/releases). I tried to use chromedriver, but it was giving errors relating to Bluetooth and I gave up.
3. Add these variables to your environment (with windows this is setx VARIABLE_NAME=VARIABLE_VALUE). This method will use Windows task scheduler to rerun a .bat file, so we need to add these variables to the command prompt. Need to use `setx` not `set` as we need the variables to persist to all future command prompts.

```bat
setx TENNIS_URL="The base url if you tried to book a court today"
setx TENNIS_DRIVER_PATH="path to the webdriver"
```

4. Install python packages with `pip install requirements.txt`
5. Book a court by opening a terminal with the correct Python interpreter and typing `python main.py username password`. This will run the default logic that we want, but to specify the date, court and time just pass these arguments in the terminal.
6. Or make a `.bat` file by running `python scheduler.py username password`. If you double click this .bat file it should open firefox and attempt to book.
7. Schedule this task with `Task Scheduler` to automate the booking process.