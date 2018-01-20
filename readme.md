# Present Finder

![alt text](https://i.imgur.com/c4Ihhdc.png "Present Finder")
Present Finder is a fullstack web application that helps users find presents for events based on their contacts' interests. When the user enters a contact's events and interests, a list of suggested presents will be generated. The user can bookmark presents, get notifications for upcoming events, see past presents they have given someone, and more!


# Features

  - Notifications for upcoming events
  - Data visualization for user's events in a year
  - Track contacts and their events
  - Search Amazon for products
  - Find presents for contacts based on interests
  - Track current, past and bookmarked presents
  - See similar products on product detail page
  
# Screenshots

![alt text](https://i.imgur.com/fzabkkr.png "User Homepage")
This is the user's homepage with a bar graph created in Chart.js. It also lists the user's contacts and events for the current month.

![alt text](https://i.imgur.com/vyEqCPL.png "Contact Details Page")
A user can enter events and interests for a contact. This page will also show you the past presents you have given that person.

![alt text](https://i.imgur.com/WbTbCis.jpg "Event Details Page")
The events details page will show you the selected, past and bookmarked presents for a particular event. The suggest presents are based on the interests entered on the contact details page.

![alt text](https://i.imgur.com/DEyAOpo.png "Product Details Page")
A user can click into a product to see details and similar products to the selected product.

### Tech

Present Finder is created with the following:

Python, PostgreSQL, SQLAlchemy, Flask, Jinja, Javascript, JQuery, Ajax, Boostrap, Chart.js, Amazon Product Advertising API, Twilio API


### Set-Up
You will need:
- Amazon Product Advertising account
- AWS account
- Twilio account

Create and launch a virtual environment
```sh
$ virtualenv env
$ source env/bin/activate
```
Install requirements
```sh
$ pip install -r requirements.txt
```
Input your Amazon keys in a file called secrets.sh
```sh
export AMAZON_ACCESS_KEY="Your Amazon access key here"
export AMAZON_SECRET_KEY="Your Amazon secret key here"
export AMAZON_ASSOC_TAG="Your Amazon associate tag"
export FLASK_SECRET_KEY="Your flask key here"
export ACCOUNT_SID="Your Twilio account sid here"
export AUTH_TOKEN="Your Twilio auth token here"
export TWILIO_NUM="Your Twilio number here"
```

Source your file into the environment
```sh
$ source secrets.sh
```
Create and seed the database
```sh
$ createdb presents
$ python seed.py
```
Launch server
```sh
$ python server.py
```
Navigate to server address.
```sh
localhost:5000
```
