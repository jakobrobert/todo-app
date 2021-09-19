from todo_app import db
from .setting import Setting

from sqlalchemy import func


class LongTermTodo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    completed = db.Column(db.Boolean, default=False)
    timestamp_created = db.Column(db.TIMESTAMP(timezone=True), default=func.now())
    timestamp_completed = db.Column(db.TIMESTAMP(timezone=True))

    @property
    def duration(self):
        # TODO total duration of all todos referencing this LT todo
        pass

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
    def add(title):
        lt_todo = LongTermTodo(title=title)
        db.session.add(lt_todo)
        db.session.commit()

    @staticmethod
    def delete(id):
        lt_todo = LongTermTodo.get(id)
        db.session.delete(lt_todo)
        db.session.commit()

    @staticmethod
    def __create_order_by_clause():
        sort_by = Setting.get("sort_long_term_todos_by")
        if sort_by is None:
            return None
        value = sort_by.value
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
            print("Unknown value for setting with key 'sort_long_term_todos_by'!")
            return None
