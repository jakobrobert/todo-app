from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import configparser

from flask import render_template, request, redirect, url_for

config = configparser.ConfigParser()
config.read("../server.ini")
URL_PREFIX = config["DEFAULT"]["URL_PREFIX"]
DATABASE_URI = config["DEFAULT"]["DATABASE_URI"]

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from models.todo import Todo
from models.todo_list import TodoList
from models.long_term_todo import LongTermTodo
from models.setting import Setting


db.create_all()
db.session.commit()


@app.route(URL_PREFIX + "/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route(URL_PREFIX + "/todo_lists", methods=["GET"])
def get_todo_lists():
    todo_lists = TodoList.get_all()
    return render_template("todo_lists.html", todo_lists=todo_lists)


@app.route(URL_PREFIX + "/todo_lists/add", methods=["POST"])
def add_todo_list():
    title = request.form.get("title")
    TodoList.add(title)
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists/<int:id>/edit-title", methods=["POST"])
def edit_todo_list_title(id):
    title = request.form.get("title")
    todo_list = TodoList.get(id)
    todo_list.set_title(title)
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists/<int:id>/delete", methods=["GET"])
def delete_todo_list(id):
    TodoList.delete(id)
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists/<int:id>", methods=["GET"])
def get_todo_list(id):
    todo_list = TodoList.get(id)
    title = todo_list.title
    todos = Todo.get_all_of_todo_list(todo_list_id=id)
    long_term_todos = LongTermTodo.get_all()
    return render_template("todo_list.html", todo_list_id=id, title=title, todos=todos, long_term_todos=long_term_todos)


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/add", methods=["POST"])
def add_todo(todo_list_id):
    title = request.form.get("title")
    Todo.add(title, todo_list_id)
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/add-by-long-term-todo", methods=["POST"])
def add_todo_by_long_term_todo(todo_list_id):
    long_term_todo_id = request.form.get("long_term_todo_id")
    Todo.add_by_long_term_todo(long_term_todo_id, todo_list_id)
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/edit-title", methods=["POST"])
def edit_todo_title(todo_id, todo_list_id):
    title = request.form.get("title")
    todo = Todo.get(todo_id)
    todo.set_title(title)
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/toggle-completed", methods=["GET"])
def toggle_todo_completed(todo_id, todo_list_id):
    todo = Todo.get(todo_id)
    todo.toggle_completed()
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/toggle_priority", methods=["GET"])
def toggle_todo_priority(todo_id, todo_list_id):
    todo = Todo.get(todo_id)
    todo.toggle_priority()
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/start", methods=["GET"])
def start_todo(todo_id, todo_list_id):
    todo = Todo.get(todo_id)
    todo.start()
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/delete", methods=["GET"])
def delete_todo(todo_id, todo_list_id):
    Todo.delete(todo_id)
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/long_term_todos", methods=["GET"])
def get_long_term_todos():
    long_term_todos = LongTermTodo.get_all()
    return render_template("long_term_todos.html", long_term_todos=long_term_todos)


@app.route(URL_PREFIX + "/long_term_todos/<int:id>", methods=["GET"])
def get_long_term_todo(id):
    long_term_todo = LongTermTodo.get(id)
    title = long_term_todo.title
    todos = Todo.get_all_of_long_term_todo(long_term_todo_id=id)
    return render_template("long_term_todo.html", title=title, todos=todos)


@app.route(URL_PREFIX + "/long_term_todos/add", methods=["POST"])
def add_long_term_todo():
    title = request.form.get("title")
    LongTermTodo.add(title)
    return redirect(url_for("get_long_term_todos"))


@app.route(URL_PREFIX + "/long_term_todos/<int:id>/edit-title", methods=["POST"])
def edit_long_term_todo_title(id):
    title = request.form.get("title")
    long_term_todo = LongTermTodo.get(id)
    long_term_todo.set_title(title)
    return redirect(url_for("get_long_term_todos"))


@app.route(URL_PREFIX + "/long_term_todos/<int:id>/toggle-completed", methods=["GET"])
def toggle_long_term_todo_completed(id):
    long_term_todo = LongTermTodo.get(id)
    long_term_todo.toggle_completed()
    return redirect(url_for("get_long_term_todos"))


@app.route(URL_PREFIX + "/long_term_todos/<int:id>/delete", methods=["GET"])
def delete_long_term_todo(id):
    LongTermTodo.delete(id)
    return redirect(url_for("get_long_term_todos"))


@app.route(URL_PREFIX + "/update_setting_for_todo_lists", methods=["GET"])
def update_setting_for_todo_lists():
    key = request.args.get("key")
    value = request.args.get("value")
    Setting.set(key, value)
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/update_setting_for_todos", methods=["GET"])
def update_setting_for_todos(todo_list_id):
    key = request.args.get("key")
    value = request.args.get("value")
    Setting.set(key, value)
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/update_setting_for_long_term_todos", methods=["GET"])
def update_setting_for_long_term_todos():
    key = request.args.get("key")
    value = request.args.get("value")
    Setting.set(key, value)
    return redirect(url_for("get_long_term_todos"))
