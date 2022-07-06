"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """test views for users"""

    def setUp(self):

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testnikki",
                                    email="nikkitest@test.com",
                                    password="testnikki",
                                    image_url=None)
        self.testuser_id = 1999
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("paul", "pauk1@test.com", "password", None)
        self.u1_id = 778
        self.u1.id = self.u1_id
        self.u2 = User.signup("joe", "joe2@test.com", "password", None)
        self.u2_id = 884
        self.u2.id = self.u2_id
        self.u3 = User.signup("michael", "michael3@test.com", "password", None)
        self.u4 = User.signup("katie", "katie4@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp


    def test_users(self):
        """can user get to followers page"""

        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@testnikki", str(resp.data))
            self.assertIn("@joe", str(resp.data))
            self.assertIn("@katie", str(resp.data))

    def test_usersearch(self):
        with self.client as c:
            resp = c.get("/users?q=test")

            self.assertIn("@testnikki", str(resp.data))
            self.assertNotIn("@katie", str(resp.data))
           

           

    def test_userpage(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertIn("@testnikki", str(resp.data))

            self.assertEqual(resp.status_code, 200)


    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.testuser_id) #paul nikki
        f2 = Follows(user_being_followed_id=self.u2_id, user_following_id=self.testuser_id) #joe nikki
        f3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.u1_id) #nikki paul

        db.session.add_all([f1,f2,f3])
        db.session.commit()

    def test_showfollowing(self):
        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/following")
            self.assertIn("@paul", str(resp.data))
            self.assertNotIn("@katie", str(resp.data))

    def test_showfollowers(self):
        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/followers")
            self.assertIn("@paul", str(resp.data))
            self.assertNotIn("@joe", str(resp.data))
            #resp = c.get(f"/users/{self.testuser_id}/followers")


    def test_unauth_following(self):
        self.setup_followers()

        with self.client as c:

            resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@katie", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))


            #resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            #resp = c.post("/messages/1984/like", follow_redirects=True)