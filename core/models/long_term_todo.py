from todo_app import db
from core.utils import Utils

from .todo import Todo
from .setting import Setting

from sqlalchemy import func
import datetime


class LongTermTodo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    completed = db.Column(db.Boolean, default=False)
    comment = db.Column(db.String(1023))
    timestamp_created = db.Column(db.TIMESTAMP(timezone=True), default=func.now())
    timestamp_completed = db.Column(db.TIMESTAMP(timezone=True))
    progress_goal = db.Column(db.Integer)

    @property
    def total_duration(self):
        todos = Todo.get_all_of_long_term_todo(self.id)
        total_duration = datetime.timedelta(seconds=0)

        for todo in todos:
            if todo.duration is not None:
                total_duration += todo.duration

        return total_duration

    @property
    def progress(self):
        todos = Todo.get_all_of_long_term_todo(self.id)

        if not todos:
            return 0

        # Find item with max timestamp. Cannot assume that already sorted.
        # Before, assumed it and just iterated through items reversed,
        # but then sometimes progress had value of an older date.
        max_timestamp = 0
        progress = 0

        for todo in todos:
            if todo.timestamp_completed:
                if not max_timestamp or todo.timestamp_completed > max_timestamp:
                    max_timestamp = todo.timestamp_completed
                    progress = todo.progress

        return progress

    @property
    def progress_in_percents(self):
        return Utils.convert_to_percents(self.progress, self.progress_goal)

    def add_todo(self, high_priority, todo_list_id):
        todo = Todo(
            title=self.title, progress=self.progress, progress_goal=self.progress_goal,
            high_priority=high_priority, long_term_todo_id=self.id, todo_list_id=todo_list_id
        )
        db.session.add(todo)
        db.session.commit()

    def toggle_completed(self):
        self.completed = not self.completed
        if self.completed:
            self.timestamp_completed = func.now()
        else:
            self.timestamp_completed = None
        db.session.commit()

    def set_title(self, title):
        self.title = title
        db.session.commit()

    def set_comment(self, comment):
        self.comment = comment
        db.session.commit()

    def set_progress_goal(self, progress_goal):
        self.progress_goal = progress_goal
        db.session.commit()

    # REMARK Non-static Wrapper methods here so can access it in template, with static methods it seems to be a bit tricky
    def convert_timedelta_to_string(self, timedelta):
        return Utils.convert_timedelta_to_string(timedelta)

    def round_decimal(self, value):
        return Utils.round_decimal(value)

    @staticmethod
    def get(id):
        return LongTermTodo.query.filter_by(id=id).first()

    @staticmethod
    def get_all():
        query = LongTermTodo.query
        order_by_clause = LongTermTodo.__create_order_by_clause()
        if order_by_clause is not None:
            query = query.order_by(order_by_clause)
        return query.all()

    @staticmethod
    def add(title, progress_goal):
        long_term_todo = LongTermTodo(title=title, progress_goal=progress_goal)
        db.session.add(long_term_todo)
        db.session.commit()
        return long_term_todo

    @staticmethod
    def delete(id):
        long_term_todo = LongTermTodo.get(id)
        db.session.delete(long_term_todo)
        db.session.commit()

    @staticmethod
    def __create_order_by_clause():
        sort_by = Setting.get("sort_long_term_todos_by")
        if sort_by is None:
            return None

        value = sort_by.value
        if value is None:
            return None

        if value == "title_ascending":
            return LongTermTodo.title.asc()
        elif value == "title_descending":
            return LongTermTodo.title.desc()
        elif value == "created_at_ascending":
            return LongTermTodo.timestamp_created.asc()
        elif value == "created_at_descending":
            return LongTermTodo.timestamp_created.desc()
        elif value == "completed_at_ascending":
            return LongTermTodo.timestamp_completed.asc()
        elif value == "completed_at_descending":
            return LongTermTodo.timestamp_completed.desc()
        else:
            raise ValueError(f"Unknown value for setting with key 'sort_long_term_todos_by': {value}")
