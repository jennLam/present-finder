"""Utility file to seed presents database."""

from sqlalchemy import func
from model import User, Contact, Interest, Event
from model import connect_to_db, db
from server import app
from datetime import datetime


def load_users():
    """Load users from user_data into database."""

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    # User.query.delete()

    # Read user_data file and insert datat
    for line in open("seed_data/user_data"):
        line = line.rstrip()
        user_id, fname, lname, username, email, password = line.split(",")

        user = User(user_id=user_id, fname=fname, lname=lname, username=username,
                    email=email, password=password)

        # We need to add to the session or it won't be stored
        db.session.add(user)

    #Once we're done, we should commit our work
    db.session.commit()


def load_contacts():
    """Load contacts from contact_data into database."""

    # Contact.query.delete()

    for line in open("seed_data/contact_data"):
        line = line.rstrip()
        contact_id, user_id, fname, lname = line.split(",")

        contact = Contact(contact_id=contact_id, user_id=user_id, fname=fname,
                          lname=lname)

        db.session.add(contact)

    db.session.commit()


def load_interests():
    """Load interests from interest_data into database."""

    # Interest.query.delete()

    for line in open("seed_data/interest_data"):
        line = line.rstrip()
        interest_id, contact_id, name, intensity = line.split(",")

        interest = Interest(interest_id=interest_id, contact_id=contact_id,
                            name=name, intensity=intensity)

        db.session.add(interest)

    db.session.commit()


def load_events():
    """Load events from event_data into database."""

    # Event.query.delete()

    for line in open("seed_data/event_data"):
        line = line.rstrip()
        event_id, contact_id, event_name, date = line.split(",")

        date = datetime.strptime(date, "%m/%d/%Y")

        event = Event(event_id=event_id, contact_id=contact_id,
                      event_name=event_name, date=date)

        db.session.add(event)

    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


def set_val_contact_id():
    """Set value for the next id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(Contact.contact_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('contacts_contact_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


def set_val_event_id():
    """Set value for the next id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(Event.event_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('events_event_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    #Import data
    load_users()
    load_contacts()
    # load_interests()
    load_events()
    set_val_user_id()
    set_val_contact_id()
    set_val_event_id()
