# WARNING This is put into root directory rather than sub-directory, because import errors
# Following errors for 3 different attempts:
# 1.    from app.todo_app import app
#       ModuleNotFoundError: No module named 'app'
# 2.    from todo_app import app
#       ModuleNotFoundError: No module named 'todo_app'
# 3.    from ..app.todo_app import app
#       ImportError: attempted relative import with no known parent package

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