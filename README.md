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

# Schedule a tasks on Windows

Lets say we want to book on "2022-03-03" at "17:00" on Court 3. We could type this into the command line, and it would run. 

```bash
python main.py username password -d 2022-03-03 -t 17:00 -c 3 --confirm
```

But we want to wait until just before midnight, so that we can book the courts as soon as they are available. 

1. So we will copy this commands into a `.bat` file and save it as "book.bat"
   1. If you double click this .bat file it should open Firefox and attempt to book.
   2. use the `--confirm` flag to click the confirm button. Leave this out if you just want to test
2. We can schedule this task with `Task Scheduler` to automate the booking process.
3. Open "Windows Task Scheduler" and create a new "Basic Task"
4. Set this up to run even when user is not logged in. Trigger it to happen every week (or whatever you need)
5. The action will be to run out `.bat` file. We have to also include the folder of the `.bat` file in the "Start in (optional)" box

If you don't specify these flags it will just use the defaults.