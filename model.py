"""Models and database functions for cars db."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()


##############################################################################


class User(db.Model):
    """User model."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    fname = db.Column(db.String(25), nullable=False)
    lname = db.Column(db.String(25), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    notification = db.Column(db.Boolean, nullable=False)

    events = db.relationship("Event", secondary="contacts", backref="user")

    def __repr__(self):
        """Provide helpful representation when printed."""

        s = "<User user_id=%s fname=%s lname=%s username=%s email=%s password=%s notification=%s>"
        return s % (self.user_id, self.fname, self.lname, self.username,
                    self.email, self.password, self.notification)


class Contact(db.Model):
    """Contact model."""

    __tablename__ = "contacts"

    contact_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(25), nullable=False)

    user = db.relationship("User", backref=db.backref("contacts"))
    interests = db.relationship("Interest", secondary="intensities", backref="contacts")

    def __repr__(self):
        """Provide helpful representation when printed."""

        s = "<Contact contact_id=%s user_id=%s fname=%s lname=%s>"
        return s % (self.contact_id, self.user_id,  self.fname, self.lname)


class Interest(db.Model):
    """Interest model."""

    __tablename__ = "interests"

    interest_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    data = db.Column(JSON)

    def __repr__(self):
        """Provide helpful representation when printed."""

        s = "<Interest interest_id=%s name=%s category=%s data=%s>"
        return s % (self.interest_id, self.name, self.category, self.data)


class Intensity(db.Model):
    """Contact model."""

    __tablename__ = "intensities"

    intensity_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.contact_id"), nullable=False)
    interest_id = db.Column(db.Integer, db.ForeignKey("interests.interest_id"), nullable=False)
    amount = db.Column(db.Boolean)

    contact = db.relationship("Contact", backref=db.backref("intensities"))
    interest = db.relationship("Interest", backref=db.backref("intensities"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        s = "<Intensity intensity_id=%s contact_id=%s interest_id=%s amount=%s>"
        return s % (self.intensity_id, self.contact_id, self.interest_id, self.amount)


class Event(db.Model):
    """Event model."""

    __tablename__ = "events"

    event_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey("contacts.contact_id"))
    event_name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime)

    contact = db.relationship("Contact", backref=db.backref("events"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        s = "<Event event_id=%s contact_id=%s event_name=%s date=%s>"
        return s % (self.event_id, self.contact_id, self.event_name, self.date)


class Status(db.Model):
    """Status model."""

    __tablename__ = "statuses"

    status_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    status_name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        s = "<Status status_id=%s status_name=%s>"
        return s % (self.status_id, self.status_name)


class Present(db.Model):
    """Present model."""

    __tablename__ = "presents"

    present_id = db.Column(db.String(20), nullable=False, primary_key=True)
    # event_id = db.Column(db.Integer, db.ForeignKey("events.event_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.status_id"))
    # status_name = db.Column(db.String(50))
    present_name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200))
    img_url = db.Column(db.String(200))

    # event = db.relationship("Event", backref=db.backref("presents"))
    user = db.relationship("User", backref=db.backref("presents"))
    status = db.relationship("Status", backref=db.backref("presents"))
    event = db.relationship("Event", secondary="presentevents", backref="presents")

    def __repr__(self):
        """Provide helpful representation when printed."""

        # s = "<Present present_id=%s event_id=%s user_id=%s status_name=%s present_name=%s url=%s img_url=%s>"
        # return s % (self.present_id, self.event_id, self.user_id, self.status_name,
        #             self.present_name, self.url, self.img_url)

        s = "<Present present_id=%s user_id=%s status_id=%s present_name=%s url=%s img_url=%s>"
        return s % (self.present_id, self.user_id, self.status_id, self.present_name,
                    self.url, self.img_url)


class PresentEvent(db.Model):
    """PresentEvent model."""

    __tablename__ = "presentevents"

    presentevent_id = db.Column(db.Integer, autoincrement=True, nullable=False, primary_key=True)
    present_id = db.Column(db.String(20), db.ForeignKey("presents.present_id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.event_id"), nullable=False)

    present = db.relationship("Present", backref=db.backref("presentevents"))
    event = db.relationship("Event", backref=db.backref("presentevents"))

    def __repr__(self):
        """Provide helpful representation when printed."""

        s = "<PresentEvents presentevent_id=%s present_id=%s event_id=%s>"
        return s % (self.presentevent_id, self.present_id, self.event_id)


##############################################################################
# Helper functions

def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///presents'
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."
