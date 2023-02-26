# WARNING This is put into root directory instead of sub-directory, because else issues with imports

import unittest

from todo_app import app
from todo_app import URL_PREFIX


class TestSmoke(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        response = self.app.get(f"{URL_PREFIX}/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_todo_lists(self):
        response = self.app.get(f"{URL_PREFIX}/todo_lists", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # TODO more sub-pages for todos

    def test_long_term_todos(self):
        response = self.app.get(f"{URL_PREFIX}/long_term_todos", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # TODO more sub-pages for long term todos
