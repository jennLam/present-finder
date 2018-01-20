import requests
from datetime import datetime
from model import User, Contact, Event, Present, Status, PresentEvent
from model import db, connect_to_db
from server import app
import schedule
from twilio.rest import Client
import os


def check_date(date1, date2, phone_number, event_name, contact_name):

    if date1.month == date2.month:
        days = date1.day - date2.day

        if days == 7:
            send_sms(phone_number, event_name, contact_name)


def send_sms(phone_number, event_name, contact_name):

    account_sid = os.environ.get("ACCOUNT_SID")
    auth_token = os.environ.get("AUTH_TOKEN")

    client = Client(account_sid, auth_token)

    body_message = "It's " + contact_name + "'s " + event_name + " in a week! Find a present now!"

    message = client.messages.create(
        to=phone_number,
        from_=os.environ.get("TWILIO_NUM"),
        body=body_message)

    print message.sid


def job():

    connect_to_db(app)

    events = db.session.query(User.notification,
                              User.email,
                              User.phone_number,
                              Contact.fname,
                              Contact.lname,
                              Event.event_name,
                              Event.date).join(Contact).join(Event).filter(User.notification == True).all()

    today_date = datetime.now()

    print "hello there"

    for event in events:
        print event

        phone_number = "+1" + event.phone_number.replace("-", "")
        check_date(event.date, today_date, phone_number, event.event_name, event.fname)

    presents = db.session.query(Present.present_id,
                                Status.status_name,
                                Event.date).join(Status).join(PresentEvent).join(Event).filter(Status.status_name == "selected").all()

    for present in presents:
        if present.date < today_date:
            pres = Present.query.get(present.Present.present_id)
            pres.status_id = 2
            db.session.commit()


schedule.every().day.at("08:00").do(job)

while True:
    schedule.run_pending()
