import unittest

from app.todo_app import app


class SmokeTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        # TODO set database uri
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        response = self.app.get("/", follow_redirects=True)