# WARNING This is put into root directory instead of sub-directory, because else issues with imports

import unittest

from todo_app import app
from todo_app import URL_PREFIX


# TODO #179 Fix smoke tests, they fail because data does not exist.
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
        response = self.app.get(f"{URL_PREFIX}/todo-lists", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_todo_list_1(self):
        response = self.app.get(f"{URL_PREFIX}/todo-lists/1", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_todo_list_1_timeline(self):
        response = self.app.get(f"{URL_PREFIX}/todo-lists/1/timeline", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_long_term_todos(self):
        response = self.app.get(f"{URL_PREFIX}/long-term-todos", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_long_term_todo_1(self):
        response = self.app.get(f"{URL_PREFIX}/long-term-todos/1", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_long_term_todo_1_statistics(self):
        response = self.app.get(f"{URL_PREFIX}/long-term-todos/1/statistics", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
