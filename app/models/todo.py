from todo_app import db
from utils import Utils

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
    long_term_todo_id = db.Column(db.Integer, db.ForeignKey("long_term_todo.id"))
    progress = db.Column(db.Integer)
    progress_goal = db.Column(db.Integer)

    @property
    def is_running(self):
        return self.timestamp_started is not None and not self.completed

    @property
    def duration(self):
        if self.timestamp_started is None or self.timestamp_completed is None:
            return None
        return self.timestamp_completed - self.timestamp_started

    @property
    def progress_in_percents(self):
        return Utils.calculate_progress_in_percents(self.progress, self.progress_goal)

    def set_title(self, title):
        self.title = title
        db.session.commit()

    def toggle_completed(self):
        self.completed = not self.completed
        if self.completed:
            self.timestamp_completed = func.now()
        else:
            self.timestamp_completed = None
        db.session.commit()

    def toggle_priority(self):
        self.high_priority = not self.high_priority
        db.session.commit()

    def set_progress(self, progress):
        self.progress = progress
        db.session.commit()

    def set_progress_goal(self, progress_goal):
        self.progress_goal = progress_goal
        db.session.commit()

    def start(self):
        self.timestamp_started = func.now()
        db.session.commit()

    def stop(self):
        self.timestamp_started = None
        db.session.commit()

    @staticmethod
    def get(id):
        return Todo.query.filter_by(id=id).first()

    @staticmethod
    def get_all_of_todo_list(todo_list_id):
        query = Todo.query.filter_by(todo_list_id=todo_list_id)
        order_by_clause = Todo.__create_order_by_clause()
        if order_by_clause is not None:
            query = query.order_by(order_by_clause)
        return query.all()

    @staticmethod
    def get_all_of_long_term_todo(long_term_todo_id):
        query = Todo.query.filter_by(long_term_todo_id=long_term_todo_id)
        order_by_clause = Todo.__create_order_by_clause()
        if order_by_clause is not None:
            query = query.order_by(order_by_clause)
        return query.all()

    @staticmethod
    def add(title, high_priority, todo_list_id):
        todo = Todo(title=title, high_priority=high_priority, todo_list_id=todo_list_id)
        db.session.add(todo)
        db.session.commit()

    @staticmethod
    def delete(id):
        todo = Todo.get(id)
        db.session.delete(todo)
        db.session.commit()

    @staticmethod
    def __create_order_by_clause():
        sort_by = Setting.get("sort_todos_by")
        if sort_by is None:
            return None

        value = sort_by.value
        if value is None:
            return None

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
            raise ValueError(f"Unknown value for setting with key 'sort_todos_by': {value}")
