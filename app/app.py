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


class TodoList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    timestamp_created = db.Column(db.TIMESTAMP(timezone=True), default=func.now())


@app.route(URL_PREFIX + "/", methods=["GET"])
def index():
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists", methods=["GET"])
def get_todo_lists():
    todo_lists = TodoList.query.all()
    return render_template("todo_lists.html", todo_lists=todo_lists)


@app.route(URL_PREFIX + "/add_todo_list", methods=["POST"])
def add_todo_list():
    title = request.form.get("title")
    new_todo = TodoList(title=title)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/delete_todo_list/<int:todo_list_id>", methods=["GET"])
def delete_todo_list(todo_list_id):
    todo = TodoList.query.filter_by(id=todo_list_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("get_todo_lists"))


# TODO add id
@app.route(URL_PREFIX + "/todo_list", methods=["GET"])
def get_todo_list():
    # TODO read title and pass to template
    # TODO read not all todos, but todos from this todo list
    todos = Todo.query.all()
    return render_template("todo_list.html", todos=todos)


@app.route(URL_PREFIX + "/add_todo", methods=["POST"])
def add_todo():
    title = request.form.get("title")
    new_todo = Todo(title=title)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("get_todo_list"))


@app.route(URL_PREFIX + "/update_todo/<int:todo_id>", methods=["GET"])
def update_todo(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.completed = not todo.completed
    if todo.completed:
        todo.timestamp_completed = func.now()
    else:
        todo.timestamp_completed = None
    db.session.commit()
    return redirect(url_for("get_todo_list"))


@app.route(URL_PREFIX + "/delete_todo/<int:todo_id>", methods=["GET"])
def delete_todo(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("get_todo_list"))


if __name__ == "__main__":
    db.create_all()
    # use 0.0.0.0 as host so the app is publicly available
    app.run(host="0.0.0.0", port=1024, debug=True)
