from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from jinja2 import StrictUndefined
from model import connect_to_db, db

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC123"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/register')
def show_register_form():
    """Show registration form."""

    return render_template("register.html")


@app.route('/register', methods=["POST"])
def get_register_info():
    """Get registration form information."""

    fname = request.form.get("fname")
    lname = request.form.get("lname")
    uname = request.form.get("uname")
    email = request.form.get("email")
    password = request.form.get("password")

    existing_user = User.query.filter_by(username=uname).first()

    if existing_user:
        new_user = User(fname=fname, lname=lname, username=uname, email=email,
                        password=password)

        db.session.add(new_user)
        db.session.commit()

        flash("Account successfully created.")
        return redirect("/")

    else:
        flash("Account already exists.")
        return redirect(request.referrer)

# @app.route('/login')
# def show_login_form():
#     """Show login form."""

#     return render_template("login.html")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')