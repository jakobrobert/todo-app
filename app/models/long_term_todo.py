from todo_app import db
from utils import Utils

from .todo import Todo
from .setting import Setting

from sqlalchemy import func
import datetime


class LongTermTodo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    completed = db.Column(db.Boolean, default=False)
    timestamp_created = db.Column(db.TIMESTAMP(timezone=True), default=func.now())
    timestamp_completed = db.Column(db.TIMESTAMP(timezone=True))
    progress_goal = db.Column(db.Integer)

    @property
    def total_duration(self):
        # TODO CLEANUP no need to sort todos here
        todos = Todo.get_all_of_long_term_todo_sorted_using_setting(self.id)
        total_duration = datetime.timedelta(seconds=0)
        for todo in todos:
            if todo.duration is not None:
                total_duration += todo.duration
        return total_duration

    @property
    def progress(self):
        todos = Todo.get_all_of_long_term_todo_sorted_using_setting(self.id)
        max_progress = None
        for todo in todos:
            if todo.progress is None:
                continue
            if max_progress is None or todo.progress > max_progress:
                max_progress = todo.progress
        return max_progress

    @property
    def progress_in_percents(self):
        return Utils.calculate_progress_in_percents(self.progress, self.progress_goal)

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

    def set_progress_goal(self, progress_goal):
        self.progress_goal = progress_goal
        db.session.commit()

    # REMARK Could be static, but not changing it because then problems to access it in template
    def convert_timedelta_to_string(self, timedelta):
        seconds_of_last_day = timedelta.seconds
        hours_of_last_day, remaining_seconds = divmod(seconds_of_last_day, 3600)
        minutes, seconds = divmod(remaining_seconds, 60)
        total_hours = timedelta.days * 24 + hours_of_last_day
        formatted_string = f"{total_hours:02}:{minutes:02}:{seconds:02}"

        return formatted_string

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

    @staticmethod
    def delete(id):
        long_term_todo = LongTermTodo.get(id)
        db.session.delete(long_term_todo)
        db.session.commit()

    # TODO CLEANUP move above static methods for consistency
    def add_todo(self, high_priority, todo_list_id):
        todo = Todo(title=self.title, long_term_todo_id=self.id, progress_goal=self.progress_goal,
                    high_priority=high_priority, todo_list_id=todo_list_id)
        db.session.add(todo)
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
