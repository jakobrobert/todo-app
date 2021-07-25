from app import db
from .setting import Setting

from sqlalchemy import func


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    completed = db.Column(db.Boolean, default=False)
    high_priority = db.Column(db.Boolean, default=False)
    timestamp_created = db.Column(db.TIMESTAMP(timezone=True), default=func.now())
    timestamp_started = db.Column(db.TIMESTAMP(timezone=True))
    timestamp_completed = db.Column(db.TIMESTAMP(timezone=True))
    todo_list_id = db.Column(db.Integer, db.ForeignKey("todo_list.id"))

    @property
    def duration(self):
        if self.timestamp_started is None or self.timestamp_completed is None:
            return None
        return self.timestamp_completed - self.timestamp_started

    @staticmethod
    def get_all_of_todo_list(todo_list_id):
        query = Todo.query.filter_by(todo_list_id=todo_list_id)
        order_by_clause = Todo.__create_order_by_clause()
        if order_by_clause is not None:
            query = query.order_by(order_by_clause)
        return query.all()

    @staticmethod
    def __create_order_by_clause():
        sort_todos_by = Setting.get("sort_todos_by")
        if sort_todos_by is None:
            return None
        value = sort_todos_by.value
        if value == "title_ascending":
            return Todo.title.asc()
        elif value == "title_descending":
            return Todo.title.desc()
        elif value == "created_at_ascending":
            return Todo.timestamp_created.asc()
        elif value == "created_at_descending":
            return Todo.timestamp_created.desc()
        elif value == "started_at_ascending":
            return Todo.timestamp_started.asc()
        elif value == "started_at_descending":
            return Todo.timestamp_started.desc()
        elif value == "completed_at_ascending":
            return Todo.timestamp_completed.asc()
        elif value == "completed_at_descending":
            return Todo.timestamp_completed.desc()
        else:
            print("Unknown value for setting with key 'sort_todos_by'!")
            return None
