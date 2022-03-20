import argparse
import logging
from datetime import datetime

import schedule

import main

logging.basicConfig(filename="schedule.log", level=logging.INFO)


def book(args):
    main.main(
        args.u,
        args.pw,
        args.day,
        args.court,
        args.time,
        args.confirm,
        args.email,
        headless=args.headless,
    )

    return True


def test_job():
    print("I'm working...")
    return True


if __name__ == "__main__":
    logging.basicConfig(filename="book.log", level=logging.INFO)
    logging.info(f"Started booking program at {datetime.now()}")

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
        type=main.str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Whether to click confirm",
    )
    parser.add_argument(
        "--email", "-e", type=str, help="Email to send confirmation email"
    )
    parser.add_argument(
        "--headless",
        type=main.str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Whether to run in headless mode",
    )
    args = parser.parse_args()

    schedule.every().saturday.at("23:58").do(book, args)

    while True:
        schedule.run_pending()
        print("waiting...")
        time.sleep(10)
