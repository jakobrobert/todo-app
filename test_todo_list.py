# WARNING This is put into root directory instead of sub-directory, because else issues with imports

import unittest

from flask import url_for

from todo_app import app
from todo_app import URL_PREFIX
from todo_app import db

from core.models.todo_list import TodoList


class TestTodoList(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.client = app.test_client()
        self.url_prefix = f"{URL_PREFIX}/todo-lists"

    def tearDown(self):
        db.session.query(TodoList).delete()
        db.session.commit()

    def test_get_todo_lists(self):
        response = self.client.get(self.url_prefix)
        self.assertEqual(response.status_code, 200)

    def test_add_todo_list(self):
        todo_lists = TodoList.get_all()
        self.assertEqual(len(todo_lists), 0)

        response = self.client.post(f"{self.url_prefix}/add")
        self.assertEqual(response.status_code, 302)

        todo_lists = TodoList.get_all()
        self.assertEqual(len(todo_lists), 1)
        todo_list = todo_lists[0]

        response = self.client.get(f"{self.url_prefix}/{todo_list.id}")
        self.assertEqual(response.status_code, 200)

    def test_edit_todo_list_title(self):
        old_title = "Old Title"
        todo_list = TodoList(title=old_title)
        db.session.add(todo_list)
        db.session.commit()

        self.assertEqual(todo_list.title, old_title)

        url = f"{self.url_prefix}/{todo_list.id}/edit-title"
        new_title = "New Title"
        response = self.client.post(url, json={"title": new_title})
        self.assertEqual(response.status_code, 302)

        # TODO test that title is correct

    def test_delete_todo_list(self):
        self.assertFalse(True)

    def test_add_todo(self):
        self.assertFalse(True)

    def test_add_todo_by_long_term_todo(self):
        self.assertFalse(True)
