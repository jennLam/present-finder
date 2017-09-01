from datetime import datetime
from model import db, User, Contact, Event, Interest, Present, Intensity, PresentEvent, Status
from sqlalchemy import extract


def get_recent_events(events, event_date):
    """Get recent events of the current month in sorted order."""

    # Get current date
    current_date = datetime.now()

    # Filter events from database where the event date is in the same month
    # but after today's day
    recent_events = events.filter(extract("month", event_date) == current_date.month,
                                  extract("year", event_date) == current_date.year,
                                  extract("day", event_date) >= current_date.day)

    # Sort events is ascending order
    ordered_recent_events = recent_events.order_by(event_date).all()

    return ordered_recent_events


def get_events_by_month(user_id):
    month_dict = {1: 0,
                  2: 0,
                  3: 0,
                  4: 0,
                  5: 0,
                  6: 0,
                  7: 0,
                  8: 0,
                  9: 0,
                  10: 0,
                  11: 0,
                  12: 0}

    events = db.session.query(Event.date,
                              User.user_id).join(Contact).join(User).filter(User.user_id == user_id)

    ordered_events = events.order_by(Event.date).all()

    for event in ordered_events:
        month_dict[event.date.month] += 1

    return month_dict


def get_user_products(user_id):
    """Get user's products."""

    products = Present.query.filter_by(user_id=user_id).all()
    return products


def get_user_events(user_id):
    """Get user's events."""

    events = db.session.query(Event.event_id, Event.contact_id,
                              Event.event_name, Event.date, Contact.fname,
                              User.user_id).join(Contact).join(User).filter(User.user_id == user_id)

    return events


def get_sidebar_info(user_id):
    """Get information to populate sidebar."""

    products = get_user_products(user_id)

    user_events = get_user_events(user_id)

    current_events = get_recent_events(user_events, Event.date)

    return {"products": products, "current_events": current_events}
