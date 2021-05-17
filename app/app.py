from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

import configparser


config = configparser.ConfigParser()
config.read("server.ini")
URL_PREFIX = config["DEFAULT"]["URL_PREFIX"]
DATABASE_URI = config["DEFAULT"]["DATABASE_URI"]

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    completed = db.Column(db.Boolean, default=False)
    timestamp_created = db.Column(db.TIMESTAMP(timezone=True), default=func.now())
    timestamp_completed = db.Column(db.TIMESTAMP(timezone=True))
    todo_list_id = db.Column(db.Integer, db.ForeignKey("todo_list.id"))


class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    timestamp_created = db.Column(db.TIMESTAMP(timezone=True), default=func.now())
    todos = db.relationship("Todo", backref="todo_list")


@app.route(URL_PREFIX + "/", methods=["GET"])
def index():
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists", methods=["GET"])
def get_todo_lists():
    todo_lists = TodoList.query.all()
    return render_template("todo_lists.html", todo_lists=todo_lists)


@app.route(URL_PREFIX + "/todo_list/<int:id>", methods=["GET"])
def get_todo_list(id):
    todo_list = TodoList.query.filter_by(id=id).first()
    todos = todo_list.todos
    return render_template("todo_list.html", title=todo_list.title, todo_list_id=id, todos=todos)


@app.route(URL_PREFIX + "/add_todo_list", methods=["POST"])
def add_todo_list():
    title = request.form.get("title")
    new_todo = TodoList(title=title)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/delete_todo_list/<int:id>", methods=["GET"])
def delete_todo_list(id):
    todo = TodoList.query.filter_by(id=id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/add_todo/<int:todo_list_id>", methods=["POST"])
def add_todo(todo_list_id):
    title = request.form.get("title")
    new_todo = Todo(title=title, todo_list_id=todo_list_id)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/update_todo/<int:id>", methods=["GET"])
def update_todo(id):
    todo = Todo.query.filter_by(id=id).first()
    todo.completed = not todo.completed
    if todo.completed:
        todo.timestamp_completed = func.now()
    else:
        todo.timestamp_completed = None
    db.session.commit()
    return redirect(url_for("get_todo_list"))


@app.route(URL_PREFIX + "/delete_todo/<int:id>", methods=["GET"])
def delete_todo(id):
    todo = Todo.query.filter_by(id=id).first()
    # TODO delete todo from the todo list
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("get_todo_list"))


if __name__ == "__main__":
    db.create_all()
    # use 0.0.0.0 as host so the app is publicly available
    app.run(host="0.0.0.0", port=1024, debug=True)
