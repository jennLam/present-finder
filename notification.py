# from flask import Flask
# import requests
from datetime import datetime
from model import User, Contact, Event, Present, Status, PresentEvent
from model import db, connect_to_db
from server import app
import schedule
# import time

# with open('first.txt', 'a') as outFile:
#     outFile.write('\n' + str(datetime.now()))


def check_date(date1, date2, event_name):
    days = date1.day - date2.day

    if days == 7:
        send_email(event_name)

# def send_email(event_name):
#     return requests.post(
#         "https://api.mailgun.net/v3/sandbox6cfd6b1c827243528fca133a8e176106.mailgun.org/messages",
#         auth=("api", "key-99d2e4b54c0fbed991048736a555b03b"),
#         data={"from": "Present Finder <postmaster@sandbox6cfd6b1c827243528fca133a8e176106.mailgun.org>",
#               "to": "Jenny Lam <jennaylam@gmail.com>",
#               "subject": "Email Notification",
#               "html": "It's" + event_name + "Go choose a present <a href='https://www.google.com>now</a>'"})

def send_email(e):
    with open('email.txt', 'a') as outFile:
        outFile.write("It's " + e + " Gooo!\n")


def job():

    # app = Flask(__name__)

    connect_to_db(app)

    events = db.session.query(User.notification,
                              Contact.fname,
                              Contact.lname,
                              Event.event_name,
                              Event.date).join(Contact).join(Event).filter(User.notification == True).all()

    # events = Event.query.filter_by(notification=True).all()
    today_date = datetime.now()

    for event in events:
        check_date(event.date, today_date, event.event_name)

    presents = db.session.query(Present.status_id,
                                Status.status_name,
                                Event.date).join(Status).join(PresentEvent).join(Event).filter(Status.status_name == "selected").all()

    for present in presents:
        if present.date < today_date:
            present.status_id = 2
            db.session.commit()


# schedule.every().day.at("11:54").do(job)
# schedule.every(1).minutes.do(job)
schedule.every().hour.do(job)

while True:
    schedule.run_pending()
