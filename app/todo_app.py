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


db.create_all()
db.session.commit()


@app.route(URL_PREFIX + "/", methods=["GET"])
def index():
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists", methods=["GET"])
def get_todo_lists():
    query = TodoList.query
    order_by_clause = create_order_by_clause_for_todo_lists()
    if order_by_clause is not None:
        query = query.order_by(order_by_clause)
    todo_lists = query.all()
    return render_template("todo_lists.html", todo_lists=todo_lists)


@app.route(URL_PREFIX + "/todo_lists/add", methods=["POST"])
def add_todo_list():
    title = request.form.get("title")
    todo_list = TodoList(title=title)
    db.session.add(todo_list)
    db.session.commit()
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists/<int:id>/edit-title", methods=["POST"])
def edit_todo_list_title(id):
    title = request.form.get("title")
    todo_list = TodoList.query.filter_by(id=id).first()
    todo_list.title = title
    db.session.commit()
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists/<int:id>/delete", methods=["GET"])
def delete_todo_list(id):
    todo_list = TodoList.query.filter_by(id=id).first()
    for todo in todo_list.todos:
        db.session.delete(todo)
    db.session.delete(todo_list)
    db.session.commit()
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists/<int:id>", methods=["GET"])
def get_todo_list(id):
    title = TodoList.query.filter_by(id=id).first().title
    query = Todo.query.filter_by(todo_list_id=id)
    order_by_clause = create_order_by_clause_for_todos()
    if order_by_clause is not None:
        query = query.order_by(order_by_clause)
    todos = query.all()
    return render_template("todo_list.html", title=title, todo_list_id=id, todos=todos)


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/add", methods=["POST"])
def add_todo(todo_list_id):
    title = request.form.get("title")
    todo = Todo(title=title, todo_list_id=todo_list_id)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/update", methods=["GET"])
def update_todo(todo_id, todo_list_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.completed = not todo.completed
    if todo.completed:
        todo.timestamp_completed = func.now()
    else:
        todo.timestamp_completed = None
    db.session.commit()
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/edit-title", methods=["POST"])
def edit_todo_title(todo_id, todo_list_id):
    title = request.form.get("title")
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.title = title
    db.session.commit()
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/start", methods=["GET"])
def start_todo(todo_id, todo_list_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.timestamp_started = func.now()
    db.session.commit()
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/delete", methods=["GET"])
def delete_todo(todo_list_id, todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/update_setting_for_todo_lists", methods=["GET"])
def update_setting_for_todo_lists():
    key = request.args.get("key")
    value = request.args.get("value")
    setting = Setting.query.filter_by(key=key).first()
    if setting is None:
        setting = Setting(key=key, value=value)
        db.session.add(setting)
        db.session.commit()
    setting.value = value
    db.session.commit()
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/update_setting_for_todos", methods=["GET"])
def update_setting_for_todos(todo_list_id):
    key = request.args.get("key")
    value = request.args.get("value")
    setting = Setting.query.filter_by(key=key).first()
    if setting is None:
        setting = Setting(key=key, value=value)
        db.session.add(setting)
        db.session.commit()
    setting.value = value
    db.session.commit()
    return redirect(url_for("get_todo_list", id=todo_list_id))


def create_order_by_clause_for_todo_lists():
    sort_todo_lists_by = Setting.query.filter_by(key="sort_todo_lists_by").first()
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


def create_order_by_clause_for_todos():
    sort_todos_by = Setting.query.filter_by(key="sort_todos_by").first()
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
