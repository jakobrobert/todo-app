# WARNING This is put into root directory instead of sub-directory, because else issues with imports

import unittest

from todo_app import app
from todo_app import URL_PREFIX

from core.models.todo_list import TodoList


class TestSmoke(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.app = app.test_client()
        # TODO set up database uri. first use real database, is fine, can change later.

    def tearDown(self):
        # TODO clear the entire database
        pass

    def test_get_todo_lists(self):
        response = self.app.get(f"{URL_PREFIX}/todo-lists", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_todo_list(self):
        todo_lists = TodoList.get_all()
        self.assertEqual(len(todo_lists), 0)

        response = self.app.post(f"{URL_PREFIX}/todo-lists/add", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
