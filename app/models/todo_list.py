from app import db
from sqlalchemy import func

class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    timestamp_created = db.Column(db.TIMESTAMP(timezone=True), default=func.now())
    todos = db.relationship("Todo", backref="todo_list")
