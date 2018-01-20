from flask import Flask, render_template, redirect, request, flash, session, g, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import User, Contact, Interest, Intensity, Event, Present, PresentEvent, Status
from model import connect_to_db, db
from functools import wraps
import json
import amazonapi
from resource import get_sidebar_info, get_events_by_month
import os
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

bcrypt = Bcrypt(app)

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
            return redirect(url_for('show_login_form'))

    return wrap


@app.route("/")
def index():
    """Homepage."""

    if g.user_id:
        return redirect("/home")

    return render_template("homepage.html")


def add_to_database(item):
    """Add item to the database."""

    db.session.add(item)
    db.session.commit()


@app.route("/register")
def show_register_form():

    return render_template("register.html")


@app.route("/register", methods=["POST"])
def process_register_info():
    """Get registration form information."""

    # Get information from registration from
    fname = request.form.get("fname")
    lname = request.form.get("lname")
    uname = request.form.get("uname")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    notification = request.form.get("notification")

    hashed_pw = bcrypt.generate_password_hash(password)

    # Get existing user in database
    existing_user = User.query.filter_by(username=uname).first()

    # Make new user
    new_user = User(fname=fname, lname=lname, username=uname, email=email, phone_number=phone,
                    password=hashed_pw, notification=notification)

    # Check database, add to database
    check_and_add(existing_user, new_user)

    return redirect("/")


@app.route("/login", methods=["POST"])
def process_login():
    """Process login."""

    username = request.form.get("username")
    password = request.form.get("password")

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        if bcrypt.check_password_hash(existing_user.password, password):
            session["user_id"] = existing_user.user_id
            session["user_name"] = existing_user.fname

            return redirect("/home")
        else:
            flash("Incorrect password.")
    else:
        flash("User does not exist.")

    return redirect(request.referrer)


@app.route("/home")
@login_required
def show_user_page():
    """Show user's homepage."""

    sidebar_info = get_sidebar_info(g.user_id)

    return render_template("home.html", user=g.current_user, current_events=sidebar_info["current_events"],
                           category_list=category_list)


def check_and_add(existing_item, item):
    """Check if an item already exists in the database and adds it if it doesn't."""

    # Check if it exists
    if existing_item:
        flash(item.__class__.__name__ + " already exists.")
        return
    # If not, add to database
    else:
        add_to_database(item)
        flash(item.__class__.__name__ + " successfully added.")


@app.route("/add-contact", methods=["POST"])
@login_required
def add_contact():
    """Add contact to database."""

    # Get information from form
    fname = request.form.get("fname")
    lname = request.form.get("lname")

    # Get existing contact with form info
    existing_contact = Contact.query.filter_by(user_id=g.user_id, fname=fname,
                                               lname=lname).first()

    # Make new contact with form info
    new_contact = Contact(user_id=g.user_id, fname=fname, lname=lname)

    # Check if existing contact is in database, add new contact if it isn't
    check_and_add(existing_contact, new_contact)

    return redirect(request.referrer)


@app.route("/contact/<contact_id>")
@login_required
def show_contact_details(contact_id):
    """Show contact details page."""

    contact = Contact.query.get(contact_id)

    sidebar_info = get_sidebar_info(g.user_id)

    contact_past_presents = db.session.query(Present).join(Status).join(PresentEvent).join(Event).join(Contact).filter(Contact.contact_id == contact_id,
                                                                                                                       Status.status_name == "past").all()

    if contact in g.current_user.contacts:

        return render_template("contact_details.html", contact=contact, products=sidebar_info["products"],
                               user=g.current_user, category_list=category_list,
                               current_events=sidebar_info["current_events"], contact_past_presents=contact_past_presents)
    else:
        flash("That is not your contact.")
        return redirect("/home")


@app.route("/add-event", methods=["POST"])
@login_required
def add_event():
    """Add event to database."""

    # Get information from form
    event_name = request.form.get("ename")
    date = request.form.get("date")
    contact_id = request.form.get("contact_id")

    # Get existing event
    existing_event = Event.query.filter_by(contact_id=contact_id,
                                           event_name=event_name).first()

    # Make new event
    new_event = Event(contact_id=contact_id, event_name=event_name, date=date)

    # Check in database, add to database
    check_and_add(existing_event, new_event)

    return redirect(request.referrer)


@app.route("/edit-event", methods=["POST"])
@login_required
def edit_event():
    """Edit event in database."""

    # Get info from form
    event_name = request.form.get("ename")
    date = request.form.get("date")
    event_id = request.form.get("event_id")

    # Get item from database
    existing_event = Event.query.filter_by(event_id=event_id).first()

    # Update the event_name and date attributes
    existing_event.event_name = event_name
    existing_event.date = date

    # Commit to make changes in database
    db.session.commit()
    flash("Event updated.")

    return redirect(request.referrer)


@app.route("/event/<event_id>")
@login_required
def show_event_details(event_id):
    """Show event details."""

    event = Event.query.get(event_id)
    interests = event.contact.interests
    product_list = []

    sidebar_info = get_sidebar_info(g.user_id)

    event_presents = db.session.query(Present,
                                      Event.event_id,
                                      Status.status_name).join(PresentEvent).join(Event).join(Status).filter(Event.event_id == event_id)

    selected = event_presents.filter(Status.status_name == "selected").all()
    past = event_presents.filter(Status.status_name == "past").all()
    bookmarked = event_presents.filter(Status.status_name == "bookmarked").all()

    for interest in interests:
        info = json.loads(interest.data)
        interest_full_name = interest.name + " " + interest.category
        product_list.append((interest_full_name, info["data"]))

    if event in g.current_user.events:

        return render_template("event_details.html", event=event, user=g.current_user,
                               product_list=product_list, selected=selected, past=past,
                               bookmarked=bookmarked, products=sidebar_info["products"],
                               current_events=sidebar_info["current_events"],
                               product_size=len(product_list))

    else:
        flash("This is not your event.")
        return redirect("/home")


@app.route("/add-interest", methods=["POST"])
@login_required
def add_interest():
    """Add interests to database."""

    # Get info from form
    contact_id = request.form.get("contact_id")
    interest_name = request.form.get("interest_name")
    category = request.form.get("category")
    amount = request.form.get("amount")

    # Get existing interest in database
    existing_interest = Interest.query.filter_by(name=interest_name,
                                                 category=category).first()

    # If it exists, check for intensity
    if existing_interest:
        # Get existing intensity in database
        existing_intensity = Intensity.query.filter_by(contact_id=contact_id,
                                                       interest_id=existing_interest.interest_id,
                                                       amount=amount).first()

        # Create new intensity
        new_intensity = Intensity(contact_id=contact_id,
                                  interest_id=existing_interest.interest_id,
                                  amount=amount)

        # Check and add intensity to database
        check_and_add(existing_intensity, new_intensity)

    # If interest does not exist
    else:
        # Search for interest through amazon api
        products = amazonapi.search(interest_name, category)

        # Get product in json
        product_info = get_json(products)

        # Make new interest
        new_interest = Interest(name=interest_name, category=category, data=product_info)

        # Add to database
        add_to_database(new_interest)

        # Make new intensity
        new_intensity = Intensity(contact_id=contact_id,
                                  interest_id=new_interest.interest_id, amount=amount)

        # Add to database
        add_to_database(new_intensity)

    return redirect(request.referrer)


@app.route("/remove-interest", methods=["POST"])
@login_required
def remove_interest():
    """Remove interest."""

    # Get info from form
    contact_id = request.form.get("contact_id")
    interest_id = request.form.get("interest_id")

    # Delete the intensity (connecting contact_id and interest_id)
    Intensity.query.filter_by(contact_id=contact_id, interest_id=interest_id).delete()
    # Commit to make changes to database
    db.session.commit()

    return redirect(request.referrer)


@app.route("/remove-interest.json", methods=["POST"])
@login_required
def remove_interest2():
    """Remove interest."""

    # Get info from form
    contact_id = request.form.get("contact")
    interest_id = request.form.get("interest")

    print contact_id, interest_id

    # Delete the intensity (connecting contact_id and interest_id)
    Intensity.query.filter_by(contact_id=contact_id, interest_id=interest_id).delete()
    # Commit to make changes to database
    db.session.commit()

    return jsonify({"interest": interest_id})


@app.route("/search.json")
@login_required
def search_stuff():

    name = request.args.get("text")
    category = request.args.get("cat")

    products = amazonapi.search(name, category)

    return get_json(products, compact=True)


def get_json(products, compact=False):
    """Return json."""

    product_list = []

    for product in products:

        prod_dict = {"id": product.asin, "title": product.title,
                     "url": product.detail_page_url, "img_url": product.medium_image_url}

        product_list.append(prod_dict)

    if compact:
        return jsonify({'data': product_list, "error": None})
    else:
        return json.dumps({'data': product_list, "error": None})


@app.route("/product.json")
@login_required
def check_bookmark():
    product_id = request.form.get("product")
    event_id = request.form.get("event")
    status_name = request.form.get("status")

    existing_product = db.session.query(Present.present_id,
                                        Status.status_name,
                                        Event.event_id).join(Status).join(PresentEvent).join(Event).filter(Present.present_id == product_id,
                                                                                                           Event.event_id == event_id)

    if existing_product.filter(Status.status_name == status_name).first():
        return jsonify({"exists": True})


@app.route("/exists.json")
@login_required
def bookmark_exists():
    event_id = request.args.get("event")
    status_name = request.args.get("status")
    bookmarked = []

    existing_products = db.session.query(Present.present_id).join(Status).join(PresentEvent).join(Event).filter(Event.event_id == event_id,
                                                                                                                Status.status_name == status_name)
    for product in existing_products:
        bookmarked.append(product[0])

    return jsonify({"bookmarked": bookmarked})


@app.route("/bookmark.json", methods=["POST"])
@login_required
def bookmark_items():

    product_id = request.form.get("product")
    event_id = request.form.get("event")
    status_name = request.form.get("status")
    image = request.form.get("image")
    url = request.form.get("url")
    title = request.form.get("title")

    # Get product from database
    existing_product = db.session.query(Present.present_id,
                                        Status.status_name,
                                        Event.event_id).join(Status).join(PresentEvent).join(Event).filter(Present.present_id == product_id,
                                                                                                           Event.event_id == event_id)

    if existing_product.filter(Status.status_name == status_name).first():
        flash("You have already liked this product.")

    elif existing_product.first():
        existing_present = Present.query.filter_by(present_id=product_id).first()
        status_id = db.session.query(Status.status_id).filter(Status.status_name == status_name).first()
        existing_present.status_id = status_id

        db.session.commit()

    else:
        status_id = db.session.query(Status.status_id).filter(Status.status_name == status_name).first()
        add_to_database(Present(present_id=product_id, status_id=status_id,
                                present_name=title, url=url,
                                img_url=image))

        add_to_database(PresentEvent(present_id=product_id, event_id=event_id))

    if len(title) > 50:
        title[0:49]

    return jsonify({'id': product_id, 'image': image, 'title': title, 'event': event_id})


@app.route("/unbookmark.json", methods=["POST"])
@login_required
def unbookmark_items():

    product_id = request.form.get("product")
    event_id = request.form.get("event")
    status_name = request.form.get("status")

    print product_id, event_id, status_name

    existing_product = db.session.query(Present.present_id,
                                        PresentEvent.presentevent_id,
                                        Status.status_name,
                                        Event.event_id).join(Status).join(PresentEvent).join(Event).filter(Present.present_id == product_id,
                                                                                                           Event.event_id == event_id,
                                                                                                           Status.status_name == status_name).first()
    if existing_product:
        PresentEvent.query.filter_by(presentevent_id=existing_product.presentevent_id).delete()
        Present.query.filter_by(present_id=product_id).delete()
        db.session.commit()

    return jsonify({'id': product_id})


@app.route("/bookmark", methods=["POST"])
@login_required
def bookmark_product():
    """Add products the user bookmarks to presents table in database."""

    # Get info from form
    product_id = request.form.get("product_id")
    event_id = request.form.get("event_id")
    status_name = request.form.get("status_name")

    # Get product from amazon api through product_id
    product = amazonapi.lookup(product_id)

    # Get product from database
    existing_product = db.session.query(Present.present_id,
                                        Status.status_name,
                                        Event.event_id).join(Status).join(PresentEvent).join(Event).filter(Present.present_id == product.asin,
                                                                                                           Event.event_id == event_id)

    if existing_product.filter(Status.status_name == status_name).first():
        flash("You have already liked this product.")

    elif existing_product.first():
        existing_present = Present.query.filter_by(present_id=product_id).first()
        status_id = db.session.query(Status.status_id).filter(Status.status_name == status_name).first()
        existing_present.status_id = status_id

        db.session.commit()

    else:
        status_id = db.session.query(Status.status_id).filter(Status.status_name == status_name).first()
        add_to_database(Present(present_id=product.asin, status_id=status_id,
                                present_name=product.title, url=product.detail_page_url,
                                img_url=product.medium_image_url))

        add_to_database(PresentEvent(present_id=product.asin, event_id=event_id))

    return redirect(request.referrer)


@app.route("/product-details/<product_id>")
@login_required
def show_product(product_id):

    event_id = request.args.get("event_id")

    sidebar_info = get_sidebar_info(g.user_id)

    product = amazonapi.lookup(product_id)

    sim_products = amazonapi.get_similar(product_id)

    return render_template("product_details.html", product=product, event_id=event_id,
                           products=sidebar_info["products"], current_events=sidebar_info["current_events"],
                           user=g.current_user, sim_products=sim_products)


@app.route('/event-nums.json')
@login_required
def num_of_events_data():
    """Return data about number of events."""

    num_of_events = get_events_by_month(g.user_id).values()

    data_dict = {
                "labels": [
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December"
                ],
                "datasets": [
                    {
                        "data": num_of_events,
                        "label": "Number of Events",
                        "backgroundColor": [
                            "#c70039",
                            "#ff5733",
                            "#ff8d1a",
                            "#ffc300",
                            "#eddd53",
                            "#add45c",
                            "#57c785",
                            "#00baad",
                            "#2a7b9b",
                            "#3d3d6b",
                            "#511849",
                            "#900c3f",
                        ],
                        "hoverBackgroundColor": [
                            "#c70039",
                            "#3ff5733",
                            "#Fff8d1a",
                            "#3ffc300",
                            "#eddd53",
                            "#add45c",
                            "#57c785",
                            "#00baad",
                            "#2a7b9b",
                            "#3d3d6b",
                            "#511849",
                            "#900c3f",
                        ]
                    }]

                }

    return jsonify(data_dict)


@app.route("/logout")
@login_required
def process_logout():
    """Process logout."""

    session.clear()

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
