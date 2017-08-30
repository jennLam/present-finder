import unittest
from server import app
from model import db, connect_to_db, example_data, User, Contact, Event
from seed import set_val_user_id, set_val_contact_id, set_val_event_id


class ServerTests(unittest.TestCase):

    def setUp(self):
        """Do before every test."""
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_index(self):
        result = self.client.get("/")
        self.assertIn("<h1>This is the homepage!</h1>", result.data)

    def test_register(self):
        result = self.client.get("/register")
        self.assertIn("Register", result.data)

    def test_login(self):
        result = self.client.get("/login")
        self.assertIn("Login", result.data)


class ServerTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Do before every test."""

        self.client = app.test_client()
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "key"

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = 1
                sess["user_name"] = 1

        connect_to_db(app, "postgresql:///testdb")

        db.create_all()
        example_data()
        set_val_user_id()
        set_val_contact_id()
        set_val_event_id()

    def tearDown(self):
        """Do after each test."""

        db.session.close()
        db.drop_all()

    def test_register(self):
        self.client.post("/register",
                         data={"fname": "Bryan",
                               "lname": "Ryan",
                               "uname": "bryan",
                               "email": "bryan@bryan.com",
                               "password": "bryan",
                               "notification": True},
                         follow_redirects=True)

        # import pdb; pdb.set_trace()

        new_user = User.query.filter_by(username="bryan").first()
        
        self.assertIsNotNone(new_user)

        # self.assertIn("User successfully added.", result.data)

    def test_login(self):
        result = self.client.post("/login",
                                  data={"username": "jane",
                                        "password": "jane"},
                                  follow_redirects=True)

        self.assertIn("Login Successful!", result.data)

    def test_logout(self):
        result = self.client.get("/logout",
                                 follow_redirects=True)

        self.assertIn("Logout Successful", result.data)

if __name__ == "__main__":
    unittest.main()
