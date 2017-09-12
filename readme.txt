Present Finder is a fullstack web application that helps users find presents for events based on their contacts' interests. When the user enters a contact's events and interests, a list of suggested presents will be generated. The user can bookmark presents, get notifications for upcoming events, see past presents they have given someone, and more!

Tech Stack
Python, PostgreSQL, SQLAlchemy, Flask, Jinja, Javascript, JQuery, Ajax, Boostrap, Chart.js, Amazon Product Advertising API, Mailgun API

You will need:

Amazon Product Advertising account
AWS account

Setup
Create and launch a virtual environment
	$ virtualenv env
	$ source env/bin/activate

Install requirements
	$ pip install -r requirements.txt

Input your Amazon keys in a file called secrets.sh
	export AMAZON_ACCESS_KEY="Your access key here"
	export AMAZON_SECRET_KEY="Your secret key here"
	export AMAZON_ASSOC_TAG="Your associate tag"

Source your file into the environment
	$ source secrets.sh

Create and seed the database
	$ createdb presents
	$ python seed.py

Launch server
	$ python server.py

Open at http://localhost:5000/