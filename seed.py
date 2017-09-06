"""Utility file to seed presents database."""

from sqlalchemy import func
from model import User, Contact, Interest, Event, Present, Intensity, Status
from model import connect_to_db, db
from server import app
from datetime import datetime
from update_pkey_seqs import update_pkey_seqs


def load_users():
    """Load users from user_data into database."""

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    # User.query.delete()

    # Read user_data file and insert datat
    for line in open("seed_data/user_data"):
        line = line.rstrip()
        user_id, fname, lname, username, email, password, notification = line.split(",")

        user = User(user_id=user_id, fname=fname, lname=lname, username=username,
                    email=email, password=password, notification=notification)

        # We need to add to the session or it won't be stored
        db.session.add(user)

    #Once we're done, we should commit our work
    db.session.commit()


def load_contacts():
    """Load contacts from contact_data into database."""

    for line in open("seed_data/contact_data"):
        line = line.rstrip()
        contact_id, user_id, fname, lname = line.split(",")

        contact = Contact(contact_id=contact_id, user_id=user_id, fname=fname,
                          lname=lname)

        db.session.add(contact)

    db.session.commit()


def load_interests():
    """Load interests from interest_data into database."""

    for line in open("seed_data/interest_data"):
        line = line.rstrip()
        interest_id, contact_id, name, intensity = line.split(",")

        interest = Interest(interest_id=interest_id, contact_id=contact_id,
                            name=name, intensity=intensity)

        db.session.add(interest)

    db.session.commit()


def load_events():
    """Load events from event_data into database."""

    for line in open("seed_data/event_data"):
        line = line.rstrip()
        event_id, contact_id, event_name, date = line.split(",")

        date = datetime.strptime(date, "%m/%d/%Y")

        event = Event(event_id=event_id, contact_id=contact_id,
                      event_name=event_name, date=date)

        db.session.add(event)

    db.session.commit()


def load_statuses():
    """Load statuses from status_data to database."""

    for line in open("seed_data/status_data"):
        line = line.rstrip()
        status_name = line

        status = Status(status_name=status_name)

        db.session.add(status)

    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    #Import data
    load_users()
    load_contacts()
    load_events()
    load_statuses()
    update_pkey_seqs()