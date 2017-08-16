from flask import Flask, render_template, redirect, request, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import User, Contact, Interest, Event, Present, Status
from model import connect_to_db, db
from datetime import datetime
from sqlalchemy import extract
# from amazon.api import AmazonAPI
import amazonapi
# from trying import make_list

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC123"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

category_list = ['All', 'Apparel', 'Appliances', 'ArtsAndCrafts', 'Automotive',
                 'Baby', 'Beauty', 'Blended', 'Books', 'Classical', 'Collectibles',
                 'DVD', 'DigitalMusic', 'Electronics', 'GiftCards', 'GourmetFood',
                 'Grocery', 'HealthPersonalCare', 'HomeGarden', 'Industrial',
                 'Jewelry', 'KindleStore', 'Kitchen', 'LawnAndGarden', 'Marketplace',
                 'MP3Downloads', 'Magazines', 'Miscellaneous', 'Music', 'MusicTracks',
                 'MusicalInstruments', 'MobileApps', 'OfficeProducts', 'OutdoorLiving',
                 'PCHardware', 'PetSupplies', 'Photo', 'Shoes', 'Software', 'SportingGoods',
                 'Tools', 'Toys', 'UnboxVideo', 'VHS', 'Video', 'VideoGames', 'Watches',
                 'Wireless', 'WirelessAccessories']


@app.before_request
def before_request():
    """Run before each route."""

    user_id = session.get("user_id")
    if user_id:
        g.current_user = User.query.get(user_id)


@app.route("/")
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/register")
def show_register_form():
    """Show registration form."""

    return render_template("register.html")


@app.route("/register", methods=["POST"])
def process_register_info():
    """Get registration form information."""

    fname = request.form.get("fname")
    lname = request.form.get("lname")
    uname = request.form.get("uname")
    email = request.form.get("email")
    password = request.form.get("password")

    existing_user = User.query.filter_by(username=uname).first()

    if existing_user:
        flash("Account already exists.")
        return redirect(request.referrer)

    else:
        new_user = User(fname=fname, lname=lname, username=uname, email=email,
                        password=password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account successfully created.")
        return redirect("/")


@app.route("/login")
def show_login_form():
    """Show login form."""

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def process_login():
    """Process login."""

    username = request.form.get("username")
    password = request.form.get("password")

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        existing_password = existing_user.password
        if existing_password == password:
            session["user_id"] = existing_user.user_id
            session["user_name"] = existing_user.fname
            flash("Login Successful!")
            return redirect("/user/" + str(session["user_id"]))
        else:
            flash("Incorrect password.")
            return redirect(request.referrer)
    else:
        flash("User does not exist.")
        return redirect(request.referrer)


@app.route("/user/<user_id>")
def show_user_page(user_id):
    """Show user page."""

    user = User.query.get(user_id)
    products = Present.query.filter(Present.event_id == None).all()

    contacts = db.session.query(Contact.contact_id).filter_by(user_id=user_id).all()

    # events = Event.query.filter(Event.contact_id.in_(contacts)).all()

    current_datetime = datetime.now()
    current_month = current_datetime.month
    current_year = current_datetime.year

    current_events = Event.query.filter(Event.contact_id.in_(contacts),
                                        extract("month", Event.date) == current_month,
                                        extract("year", Event.date) == current_year).all()

    return render_template("home.html", user=user, products=products,
                           current_events=current_events)


@app.route("/add-contact", methods=["POST"])
def add_contact():
    """Add contact to database."""

    fname = request.form.get("fname")
    lname = request.form.get("lname")
    user_id = session["user_id"]

    existing_contact = Contact.query.filter_by(user_id=user_id, fname=fname, lname=lname).first()

    if existing_contact:
        flash("Contact already exists.")
        return redirect(request.referrer)
    else:
        new_contact = Contact(user_id=user_id, fname=fname, lname=lname)
        db.session.add(new_contact)
        db.session.commit()
        flash("Contact successfully added.")
        return redirect(request.referrer)


@app.route("/contact")
def show_contacts():
    """Show a list of contacts."""

    user_id = session["user_id"]
    user = User.query.get(user_id)

    return render_template("contacts.html", user=user)


@app.route("/contact/<contact_id>")
def show_contact_details(contact_id):
    """Show contact page."""

    user_id = session["user_id"]
    contact = Contact.query.get(contact_id)
    user = User.query.get(user_id)

    return render_template("contact_details.html", contact=contact, user=user)


# @app.route("/add-event", methods=["GET"])
# def show_event_form():
#     """Show form to add event."""

#     return render_template("add_event.html")


@app.route("/add-event", methods=["POST"])
def add_event():
    """Add event to database."""

    event_name = request.form.get("ename")
    date = request.form.get("date")
    contact_id = request.form.get("contact_id")

    existing_event = Event.query.filter_by(contact_id=contact_id,
                                           event_name=event_name).first()

    if existing_event:
        flash("event already exists.")
        return redirect(request.referrer)
    else:
        event = Event(contact_id=contact_id, event_name=event_name, date=date)
        db.session.add(event)
        db.session.commit()
        flash("Event successfully added.")
        return redirect(request.referrer)


@app.route("/event")
def show_events():
    """Show a list of events."""

    user_id = session.get("user_id")
    contacts = db.session.query(Contact.contact_id).filter_by(user_id=user_id).all()
    events = Event.query.filter(Event.contact_id.in_(contacts)).all()

    return render_template("events.html", events=events)


@app.route("/event/<event_id>")
def show_event_details(event_id):
    """Show event details."""

    event = Event.query.get(event_id)
    interests = event.contact.interests
    product_list = []

    prods= Present.query.filter(Present.event_id == event_id).all()

    for interest in interests:
        products = amazonapi.search(interest.name, interest.category)
        for product in products:

            product_list.append(product)

    return render_template("event_details.html", event=event,
                           product_list=product_list, prods=prods)


@app.route("/add-interest", methods=["GET"])
def show_interest():
    """Show interest form."""

    contact_id = request.args.get("contact_id")

    contact = Contact.query.get(contact_id)

    interests = contact.interests

    return render_template("interest.html", contact=contact, category_list=category_list,
                           interests=interests)


@app.route("/add-interest", methods=["POST"])
def add_interest():
    """Add interests to database."""

    contact_id = request.form.get("contact_id")
    interest_name = request.form.get("interest_name")
    category = request.form.get("category")

    existing_interest = Interest.query.filter_by(name=interest_name).first()

    if existing_interest:
        flash("Interest already exists.")
        return redirect(request.referrer)
    else:
        new_interest = Interest(contact_id=contact_id, name=interest_name,
                                category=category)

        db.session.add(new_interest)
        db.session.commit()
        flash("Interest successfully added.")
        return redirect(request.referrer)


# def test_search():

#     my_list = make_list()
#     product_list = []
#     p_list = []

#     for item in my_list:

#         product = test.search(item, "All")
#         product_list.append(product)

#     for prod in product_list:
#         for p in prod:
#             p_list.append(p)

#     return p_list


@app.route("/search")
def search_amazon():
    """Search Amazon for products."""

    name = request.args.get("name")
    category = request.args.get("category")

    products = amazonapi.search(name, category)

    return render_template("search.html", products=products)


@app.route("/similar")
def find_similar():
    """Find similar products."""

    product = request.args.get("product")
    products = amazonapi.get_similar(product)

    return render_template("similar.html", products=products)


@app.route("/like", methods=["POST"])
def like_product():
    """Add products the user likes to presents table in database."""

    like = request.form.get("like")
    event_id = request.form.get("event_id")
    print event_id

    product = amazonapi.lookup(like)

    existing_product = Present.query.filter_by(present_id=product.asin, event_id=event_id).first()

    if existing_product:
        flash("You have already liked this product.")
    else:
        new_product = Present(present_id=product.asin, event_id=event_id,
                              present_name=product.title, url=product.detail_page_url,
                              img_url=product.medium_image_url)

        db.session.add(new_product)
        db.session.commit()

    return redirect(request.referrer)


@app.route("/logout")
def process_logout():
    """Process logout."""

    session["user_id"] = ""
    session["user_name"] = ""
    flash("Logout Successful.")
    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
