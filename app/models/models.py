from app import db
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


class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    timestamp_created = db.Column(db.TIMESTAMP(timezone=True), default=func.now())
    todos = db.relationship("Todo", backref="todo_list")


class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255))
    value = db.Column(db.String(255))
