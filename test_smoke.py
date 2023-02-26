# WARNING This is put into root directory instead of sub-directory, because else issues with imports

import unittest

from todo_app import app


class TestSmoke(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        # TODO set database uri
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
