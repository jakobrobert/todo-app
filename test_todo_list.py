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
        #db.session.query(TodoList).delete()
        #db.session.commit()
        pass

    def test_get_todo_lists(self):
        response = self.client.get(self.url_prefix)
        self.assertEqual(response.status_code, 200)

    def test_get_todo_list(self):
        # TODO add todo list to database, remember the id
        # TODO get request for this id, check response success
        pass

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
        todo_list_id = todo_list.id

        url = f"{self.url_prefix}/{todo_list_id}/edit-title"
        new_title = "New Title"
        response = self.client.post(url, json={"title": new_title})
        self.assertEqual(response.status_code, 302)

        # TODO fix error  sqlalchemy.orm.exc.DetachedInstanceError
        updated_todo_list = TodoList.get(todo_list_id)
        #self.assertEqual(-1, updated_todo_list.id)
        self.assertEqual(updated_todo_list.title, new_title)

    def test_delete_todo_list(self):
        # TODO
        pass

    def test_add_todo(self):
        # TODO
        pass

    def test_add_todo_by_long_term_todo(self):
        # TODO
        pass
