from app import db # TODO make all paths relative? change to ..
from .setting import Setting

from sqlalchemy import func


class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    timestamp_created = db.Column(db.TIMESTAMP(timezone=True), default=func.now())
    todos = db.relationship("Todo", backref="todo_list")

    @staticmethod
    def get_all():
        query = TodoList.query
        order_by_clause = TodoList.create_order_by_clause_for_todo_lists()
        if order_by_clause is not None:
            query = query.order_by(order_by_clause)
        return query.all()

    # TODO simplify name
    @staticmethod
    def create_order_by_clause_for_todo_lists():
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
