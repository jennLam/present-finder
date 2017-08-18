from flask import g, session
import requests
from datetime import datetime

def check_date():
    days = event_date - today_date

    if days == 7:
        send_email()


def send_email(name, event):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox6cfd6b1c827243528fca133a8e176106.mailgun.org/messages",
        auth=("api", "key-99d2e4b54c0fbed991048736a555b03b"),
        data={"from": "Present Finder <postmaster@sandbox6cfd6b1c827243528fca133a8e176106.mailgun.org>",
              "to": "Jenny Lam <jennaylam@gmail.com>",
              "subject": "Email Notification",
              "html": "It's " + name + "'s " + event + "Go choose a present <a href='https://www.google.com>now</a>'"})


