# WARNING This is put into root directory instead of sub-directory, because else issues with imports

import unittest

from todo_app import app
from todo_app import URL_PREFIX
from todo_app import db

from core.models.todo_list import TodoList
from core.models.todo import Todo
from core.models.long_term_todo import LongTermTodo


class TestTodoList(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        self.client = app.test_client()
        self.url_prefix = f"{URL_PREFIX}/todo-lists"

    def tearDown(self):
        # Wanted to use db.drop_all() instead, but then tests fail because tables do not exist
        # Seems like they are not re-created for each test as assumed
        db.session.query(Todo).delete()
        db.session.query(TodoList).delete()
        db.session.commit()

    def test_get_todo_lists(self):
        self.__send_get_request_and_assert_success(self.url_prefix)

    def test_get_todo_list(self):
        todo_list = TodoList.add()

        url = f"{self.url_prefix}/{todo_list.id}"
        self.__send_get_request_and_assert_success(url)

    def test_add_todo_list(self):
        todo_lists = TodoList.get_all()
        self.assertEqual(len(todo_lists), 0)

        url = f"{self.url_prefix}/add"
        self.__send_post_request_and_assert_success(url)

        todo_lists = TodoList.get_all()
        self.assertEqual(len(todo_lists), 1)

    def test_delete_todo_list(self):
        todo_list = TodoList.add()
        todo_list_id = todo_list.id  # Need to remember id, else DetachedInstanceError below

        todo_lists = TodoList.get_all()
        self.assertEqual(len(todo_lists), 1)

        # TODO #48 should be DELETE method, NOT GET
        url = f"{self.url_prefix}/{todo_list_id}/delete"
        self.__send_get_request_and_assert_success(url)

        todo_lists = TodoList.get_all()
        self.assertEqual(len(todo_lists), 0)

    def test_edit_todo_list_title(self):
        old_title = "Old Title"
        todo_list = TodoList.add(old_title)
        todo_list_id = todo_list.id  # Need to remember id, else DetachedInstanceError below

        self.assertEqual(todo_list.title, old_title)

        # TODO #48 maybe should be method PATCH instead of POST because changing existing resource
        url = f"{self.url_prefix}/{todo_list_id}/edit-title"
        new_title = "New Title"
        data = {"title": new_title}
        self.__send_post_request_and_assert_success(url, data)

        updated_todo_list = TodoList.get(todo_list_id)
        self.assertEqual(updated_todo_list.title, new_title)

    def test_add_todo(self):
        todo_list = TodoList.add()
        todo_list_id = todo_list.id  # Need to remember id, else DetachedInstanceError below

        todos = Todo.get_all_of_todo_list(todo_list_id)
        self.assertEqual(len(todos), 0)

        url = f"{self.url_prefix}/{todo_list_id}/todos/add"
        self.__send_post_request_and_assert_success(url)

        todos = Todo.get_all_of_todo_list(todo_list_id)
        self.assertEqual(len(todos), 1)

    def test_delete_todo(self):
        todo_list = TodoList.add()
        todo_list_id = todo_list.id # Need to remember id, else DetachedInstanceError below
        todo = Todo.add(title=None, high_priority=False, todo_list_id=todo_list_id)
        todo_id = todo.id

        todos = Todo.get_all_of_todo_list(todo_list_id)
        self.assertEqual(len(todos), 1)

        # TODO #48 should be DELETE method, NOT GET
        url = f"{self.url_prefix}/{todo_list_id}/todos/{todo_id}/delete"
        self.__send_get_request_and_assert_success(url)

        todos = Todo.get_all_of_todo_list(todo_list_id)
        self.assertEqual(len(todos), 0)

    def test_add_todo_by_long_term_todo(self):
        todo_list = TodoList.add()
        todo_list_id = todo_list.id  # Need to remember id, else DetachedInstanceError below
        long_term_todo = LongTermTodo.add(title=None, progress_goal=None)
        long_term_todo_id = long_term_todo.id  # Need to remember id, else DetachedInstanceError below

        todos = Todo.get_all_of_todo_list(todo_list_id)
        self.assertEqual(len(todos), 0)

        url = f"{self.url_prefix}/{todo_list_id}/todos/add-by-long-term-todo"
        data = {"long_term_todo_id": long_term_todo_id}
        self.__send_post_request_and_assert_success(url, data)

        todos = Todo.get_all_of_todo_list(todo_list_id)
        self.assertEqual(len(todos), 1)
        todo = todos[0]
        self.assertEqual(todo.long_term_todo_id, long_term_todo_id)

    def test_edit_todo_title(self):
        todo_list = TodoList.add()
        old_title = "Old Title"
        todo = Todo.add(title=old_title, high_priority=False, todo_list_id=todo_list.id)
        todo_id = todo.id  # Need to remember id, else DetachedInstanceError below

        self.assertEqual(todo.title, old_title)

        # TODO #48 maybe should be method PATCH because changing existing resource
        url = f"{self.url_prefix}/{todo_list.id}/todos/{todo_id}/edit-title"
        new_title = "New Title"
        data = {"title": new_title}
        self.__send_post_request_and_assert_success(url, data)

        updated_todo = Todo.get(todo_id)
        self.assertEqual(updated_todo.title, new_title)

    def test_toggle_todo_completed(self):
        todo_list = TodoList.add()
        todo = Todo.add(title=None, high_priority=False, todo_list_id=todo_list.id)
        todo_id = todo.id  # Need to remember id, else DetachedInstanceError below

        self.assertEqual(todo.completed, False)

        # TODO #48 maybe should be method PATCH because changing existing resource, but definitely NOT GET
        url = f"{self.url_prefix}/{todo_list.id}/todos/{todo_id}/toggle-completed"
        self.__send_get_request_and_assert_success(url)

        updated_todo = Todo.get(todo_id)
        self.assertEqual(updated_todo.completed, True)

    def test_toggle_todo_priority(self):
        todo_list = TodoList.add()
        todo = Todo.add(title=None, high_priority=False, todo_list_id=todo_list.id)
        todo_id = todo.id  # Need to remember id, else DetachedInstanceError below

        self.assertEqual(todo.high_priority, False)

        # TODO #48 maybe should be method PATCH because changing existing resource, but definitely NOT GET
        url = f"{self.url_prefix}/{todo_list.id}/todos/{todo_id}/toggle-priority"
        self.__send_get_request_and_assert_success(url)

        updated_todo = Todo.get(todo_id)
        self.assertEqual(updated_todo.high_priority, True)

    def test_edit_todo_comment(self):
        todo_list = TodoList.add()
        todo = Todo.add(title=None, high_priority=False, todo_list_id=todo_list.id)
        todo_id = todo.id  # Need to remember id, else DetachedInstanceError below
        old_comment = "Old Comment"
        todo.comment = old_comment

        self.assertEqual(todo.comment, old_comment)

        # TODO #48 maybe should be method PATCH because changing existing resource
        url = f"{self.url_prefix}/{todo_list.id}/todos/{todo_id}/edit-comment"
        new_comment = "New Comment"
        data = {"comment": new_comment}
        self.__send_post_request_and_assert_success(url, data)

        updated_todo = Todo.get(todo_id)
        self.assertEqual(updated_todo.comment, new_comment)

    def test_edit_todo_progress(self):
        todo_list = TodoList.add()
        todo = Todo.add(title=None, high_priority=False, todo_list_id=todo_list.id)
        todo_id = todo.id  # Need to remember id, else DetachedInstanceError below
        old_progress = 42
        todo.progress = old_progress

        self.assertEqual(todo.progress, old_progress)

        # TODO #48 maybe should be method PATCH because changing existing resource
        url = f"{self.url_prefix}/{todo_list.id}/todos/{todo_id}/edit-progress"
        new_progress = 69
        data = {"progress": new_progress}
        self.__send_post_request_and_assert_success(url, data)

        updated_todo = Todo.get(todo_id)
        self.assertEqual(updated_todo.progress, new_progress)

    def test_start_and_stop_todo(self):
        # REMARK Testing 2 endpoints in one test is not clean, but they are closely related.
        # Should be fine for now, currently not testing details like duration anyway

        todo_list = TodoList.add()
        todo_list_id = todo_list.id  # Need to remember id, else DetachedInstanceError below
        todo = Todo.add(title=None, high_priority=False, todo_list_id=todo_list.id)
        todo_id = todo.id  # Need to remember id, else DetachedInstanceError below

        self.assertTrue(todo.timestamp_started is None)

        # TODO #48 maybe should be method PATCH because changing existing resource, but definitely NOT GET
        url = f"{self.url_prefix}/{todo_list_id}/todos/{todo_id}/start"
        self.__send_get_request_and_assert_success(url)

        updated_todo = Todo.get(todo_id)
        self.assertTrue(updated_todo.timestamp_started is not None)

        # TODO #48 maybe should be method PATCH because changing existing resource, but definitely NOT GET
        url = f"{self.url_prefix}/{todo_list_id}/todos/{todo_id}/stop"
        self.__send_get_request_and_assert_success(url)

        updated_todo = Todo.get(todo_id)
        self.assertTrue(updated_todo.timestamp_started is None)

    def __send_get_request_and_assert_success(self, url):
        response = self.client.get(url, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def __send_post_request_and_assert_success(self, url, data=None):
        response = self.client.post(url, data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
