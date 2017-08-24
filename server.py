from flask import Flask, render_template, redirect, request, flash, session, g, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import User, Contact, Interest, Intensity, Event, Present, PresentEvent, Status
from model import connect_to_db, db
from datetime import datetime
from sqlalchemy import extract
from functools import wraps
import json
import amazonapi

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

    g.user_id = session.get("user_id")
    if g.user_id:
        g.current_user = User.query.get(g.user_id)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if g.user_id:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('show_login_form'))

    return wrap


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
    notification = request.form.get("notification")

    existing_user = User.query.filter_by(username=uname).first()

    if existing_user:
        flash("Account already exists.")
        return redirect(request.referrer)

    else:
        new_user = User(fname=fname, lname=lname, username=uname, email=email,
                        password=password, notification=notification)

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
@login_required
def show_user_page(user_id):
    """Show user page."""

    # user = User.query.get(user_id)
    products = Present.query.filter_by(user_id=user_id).all()

    contacts = db.session.query(Contact.contact_id).filter_by(user_id=user_id).all()

    # events = Event.query.filter(Event.contact_id.in_(contacts)).all()

    current_datetime = datetime.now()
    current_month = current_datetime.month
    current_year = current_datetime.year

    current_events = Event.query.filter(Event.contact_id.in_(contacts),
                                        extract("month", Event.date) == current_month,
                                        extract("year", Event.date) == current_year).all()

    return render_template("home.html", user=g.current_user, products=products,
                           current_events=current_events, category_list=category_list)


@app.route("/add-contact", methods=["POST"])
def add_contact():
    """Add contact to database."""

    fname = request.form.get("fname")
    lname = request.form.get("lname")

    existing_contact = Contact.query.filter_by(user_id=g.user_id, fname=fname,
                                               lname=lname).first()

    if existing_contact:
        flash("Contact already exists.")
        return redirect(request.referrer)
    else:
        new_contact = Contact(user_id=g.user_id, fname=fname, lname=lname)
        db.session.add(new_contact)
        db.session.commit()
        flash("Contact successfully added.")
        return redirect(request.referrer)


@app.route("/contact")
@login_required
def show_contacts():
    """Show a list of contacts."""

    return render_template("contacts.html", user=g.current_user)


@app.route("/contact/<contact_id>")
def show_contact_details(contact_id):
    """Show contact page."""

    # user_id = session["user_id"]
    contact = Contact.query.get(contact_id)
    # user = User.query.get(user_id)

    return render_template("contact_details.html", contact=contact,
                           user=g.current_user, category_list=category_list)


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


@app.route("/edit-event", methods=["POST"])
def edit_event():
    """Edit event in database."""

    event_name = request.form.get("ename")
    date = request.form.get("date")
    event_id = request.form.get("event_id")

    existing_event = Event.query.filter_by(event_id=event_id).first()

    existing_event.event_name = event_name
    existing_event.date = date

    db.session.commit()
    flash("Event updated.")
    return redirect(request.referrer)


@app.route("/event")
@login_required
def show_events():
    """Show a list of events."""

    return render_template("events.html", events=g.current_user.events)


@app.route("/notification", methods=["POST"])
def set_notification():
    reminder = request.form.get("reminder")

    for contact in g.current_user.contacts:
        for event in contact.events:
            event.notification = reminder

    db.session.commit()

    for contact in g.current_user.contacts:
        print contact.events

    return redirect(request.referrer)


@app.route("/event/<event_id>")
def show_event_details(event_id):
    """Show event details."""

    event = Event.query.get(event_id)
    interests = event.contact.interests
    product_list = []

    presents = db.session.query(Present,
                                Event.event_id,
                                Status.status_name).join(PresentEvent).join(Event).join(Status).filter(Event.event_id == event_id)

    selected = presents.filter(Status.status_name == "selected").all()
    past = presents.filter(Status.status_name == "past").all()
    bookmarked = presents.filter(Status.status_name == "bookmarked").all()

    for interest in interests:
        products = amazonapi.search_limit(10, interest.name, interest.category)

        for product in products:

            product_list.append(product)

    return render_template("event_details.html", event=event,
                           product_list=product_list, selected=selected, past=past,
                           bookmarked=bookmarked)


# @app.route("/add-interest", methods=["GET"])
# def show_interest():
#     """Show interest form."""

#     contact_id = request.args.get("contact_id")

#     contact = Contact.query.get(contact_id)

#     interests = contact.intensities

#     return render_template("interest.html", contact=contact, category_list=category_list,
#                            interests=interests)


@app.route("/add-interest", methods=["POST"])
def add_interest():
    """Add interests to database."""

    contact_id = request.form.get("contact_id")
    interest_name = request.form.get("interest_name")
    category = request.form.get("category")
    amount = request.form.get("amount")

    existing_interest = Interest.query.filter_by(name=interest_name,
                                                 category=category).first()

    if existing_interest:
        existing_intensity = Intensity.query.filter_by(contact_id=contact_id,
                                                       interest_id=existing_interest.interest_id,
                                                       amount=amount).first()
        if existing_intensity:
            flash("Interest already exists.")
            return redirect(request.referrer)
        else:
            new_intensity = Intensity(contact_id=contact_id,
                                      interest_id=existing_interest.interest_id,
                                      amount=amount)
            db.session.add(new_intensity)
            db.session.commit()
            flash("Interest successfully added.")
            return redirect(request.referrer)
    else:
        new_interest = Interest(name=interest_name, category=category)
        db.session.add(new_interest)
        db.session.commit()
        new_intensity = Intensity(contact_id=contact_id,
                                  interest_id=new_interest.interest_id, amount=True)
        db.session.add(new_intensity)
        db.session.commit()
        flash("Interest successfully added.")
        return redirect(request.referrer)


@app.route("/remove-interest", methods=["POST"])
def remove_interest():
    """Remove interest."""

    contact_id = request.form.get("contact_id")
    interest_id = request.form.get("interest_id")

    # intensity = Intensity.query.filter_by(contact_id=contact_id, interest_id=interest_id)

    # if intensity.first():
    #     intensity.delete()
    #     db.session.commit()
    #     flash("Interest removed.")

    # else:
    #     flash("Interest does not exist.")

    Intensity.query.filter_by(contact_id=contact_id, interest_id=interest_id).delete()
    db.session.commit()

    return redirect(request.referrer)


@app.route("/search2")
def search2():
    """Test search."""

    return render_template("search2.html", category_list=category_list)


@app.route("/search.json")
def search_stuff():

    name = request.args.get("text")
    category = request.args.get("cat")

    products = amazonapi.search(name, category)

    return get_json(products)

    # product_list = []

    # for product in products:
    #     # prod_dict = product.get_attributes(["Title"])

    #     prod_dict = {"id": product.asin, "title": product.title,
    #                  "url": product.detail_page_url, "img_url": product.medium_image_url}

    #     product_list.append(prod_dict)

    # return jsonify({'data': product_list, "error": None})


def get_json(products):
    """Return json."""

    product_list = []

    for product in products:
        # prod_dict = product.get_attributes(["Title"])

        prod_dict = {"id": product.asin, "title": product.title,
                     "url": product.detail_page_url, "img_url": product.medium_image_url}

        product_list.append(prod_dict)

    return jsonify({'data': product_list, "error": None})




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


@app.route("/bookmark", methods=["POST"])
def bookmark_product():
    """Add products the user bookmarks to presents table in database."""

    bookmark = request.form.get("bookmark")
    event_id = request.form.get("event_id")
    # print event_id

    product = amazonapi.lookup(bookmark)

    # existing_product = Present.query.filter_by(present_id=product.asin, event_id=event_id).first()

    existing_product = db.session.query(Present.present_id,
                                        Event.event_id).join(PresentEvent).join(Event).filter(Present.present_id == product.asin, Event.event_id == event_id).first()

    if existing_product:
        flash("You have already liked this product.")
    else:
        status_id = db.session.query(Status.status_id).filter(Status.status_name == "bookmarked").first()
        new_product = Present(present_id=product.asin, status_id=status_id, present_name=product.title,
                              url=product.detail_page_url, img_url=product.medium_image_url)

        db.session.add(new_product)
        db.session.commit()

        new_presentevent = PresentEvent(present_id=product.asin, event_id=event_id)

        db.session.add(new_presentevent)
        db.session.commit()

    return redirect(request.referrer)


@app.route("/product-details")
def show_product():
    return render_template("product_details.html")


@app.route("/logout")
@login_required
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
