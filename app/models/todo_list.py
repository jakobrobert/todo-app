from todo_app import db
from .setting import Setting
from .todo import Todo

from sqlalchemy import func


class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    timestamp_created = db.Column(db.TIMESTAMP(timezone=True), default=func.now())
    todos = db.relationship("Todo", backref="todo_list") # TODO is this needed?

    def set_title(self, title):
        self.title = title
        db.session.commit()

    def get_todos(self):
        return Todo.get_all_of_todo_list(todo_list_id=self.id)

    @staticmethod
    def get(id):
        return TodoList.query.filter_by(id=id).first()

    @staticmethod
    def get_all():
        query = TodoList.query
        order_by_clause = TodoList.__create_order_by_clause()
        if order_by_clause is not None:
            query = query.order_by(order_by_clause)
        return query.all()

    @staticmethod
    def add(title):
        todo_list = TodoList(title=title)
        db.session.add(todo_list)
        db.session.commit()

    @staticmethod
    def delete(id):
        todo_list = TodoList.get(id)
        for todo in todo_list.todos:
            db.session.delete(todo)
        db.session.delete(todo_list)
        db.session.commit()

    @staticmethod
    def __create_order_by_clause():
        sort_todo_lists_by = Setting.get("sort_todo_lists_by")
        if sort_todo_lists_by is None:
            return None
        value = sort_todo_lists_by.value
        if value == "title_ascending":
            return TodoList.title.asc()
        elif value == "title_descending":
            return TodoList.title.desc()
        elif value == "created_at_ascending":
            return TodoList.timestamp_created.asc()
        elif value == "created_at_descending":
            return TodoList.timestamp_created.desc()
        else:
            print("Unknown value for setting with key 'sort_todo_lists_by'!")
            return None
