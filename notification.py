import requests
from datetime import datetime
from model import User, Contact, Event, Present, Status, PresentEvent
from model import db, connect_to_db
from server import app
import schedule
import os


def check_date(date1, date2, email, event_name, contact_name):
    days = date1.day - date2.day

    if days == 7:
        send_email(event_name, contact_name)

def send_email(email, event_name, contact_name):
    return requests.post(
        "https://api.mailgun.net/v3/sandbox6cfd6b1c827243528fca133a8e176106.mailgun.org/messages",
        auth=("api", os.environ["MAILGUN_API_KEY"]),
        data={"from": "Present Finder <postmaster@sandbox6cfd6b1c827243528fca133a8e176106.mailgun.org>",
              "to": "User <" + email + ">",
              "subject": "You have an event coming up!",
              "html": "It's " + contact_name + "'s " + event_name + " in a week! Find a present <a href='http://localhost:5000'>now</a>!"})

def job():

    connect_to_db(app)

    events = db.session.query(User.notification,
                              User.email,
                              Contact.fname,
                              Contact.lname,
                              Event.event_name,
                              Event.date).join(Contact).join(Event).filter(User.notification == True).all()

    today_date = datetime.now()

    for event in events:
        check_date(event.date, today_date, event.email, event.event_name, event.fname)

    presents = db.session.query(Present.present_id,
                                Status.status_name,
                                Event.date).join(Status).join(PresentEvent).join(Event).filter(Status.status_name == "selected").all()

    # for present in presents:
    #     if present.date < today_date:
    #         pres = Present.query.get(present.Present.present_id)
    #         pres.status_id = 2
    #         db.session.commit()


schedule.every().day.at("11:54").do(job)

while True:
    schedule.run_pending()
