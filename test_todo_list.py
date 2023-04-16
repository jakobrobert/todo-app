# WARNING This is put into root directory instead of sub-directory, because else issues with imports

import unittest

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
        # Wanted to use db.drop_all() instead, but then tests fail because tables do not exist
        # Seems like they are not re-created for each test as assumed
        db.session.query(TodoList).delete()
        db.session.commit()

    def test_get_todo_lists(self):
        response = self.client.get(self.url_prefix)
        self.assertEqual(response.status_code, 200)

    def test_get_todo_list(self):
        title = "Test Title"
        todo_list = TodoList.add(title)
        todo_list_id = todo_list.id

        url = f"{self.url_prefix}/{todo_list_id}"
        response = self.client.get(url)
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
        todo_list = TodoList.add(old_title)
        todo_list_id = todo_list.id

        self.assertEqual(todo_list.title, old_title)

        url = f"{self.url_prefix}/{todo_list_id}/edit-title"
        new_title = "New Title"
        response = self.client.post(url, data={"title": new_title})
        self.assertEqual(response.status_code, 302)

        updated_todo_list = TodoList.get(todo_list_id)
        self.assertEqual(updated_todo_list.title, new_title)

    def test_delete_todo_list(self):
        todo_list = TodoList.add()
        todo_list_id = todo_list.id

        found_todo_list = TodoList.get(todo_list_id)
        self.assertTrue(found_todo_list is not None)

        # TODO CLEANUP should be DELETE method, NOT GET. Will change in #48
        url = f"{self.url_prefix}/{todo_list_id}/delete"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        found_todo_list = TodoList.get(todo_list_id)
        self.assertTrue(found_todo_list is None)

    def test_add_todo(self):
        # TODO
        self.assertTrue(False, "TODO")

    def test_add_todo_by_long_term_todo(self):
        # TODO
        self.assertTrue(False, "TODO")
