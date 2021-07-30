from . import db
from . import app
from . import URL_PREFIX

from .models.todo import Todo
from .models.todo_list import TodoList
from .models.setting import Setting

from flask import render_template, request, redirect, url_for


db.create_all()
db.session.commit()


@app.route(URL_PREFIX + "/", methods=["GET"])
def index():
    return redirect(url_for("get_todo_lists"))


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
    todos = todo_list.get_todos()
    return render_template("todo_list.html", todo_list_id=id, title=title, todos=todos)


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/add", methods=["POST"])
def add_todo(todo_list_id):
    title = request.form.get("title")
    Todo.add(title, todo_list_id)
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/edit-title", methods=["POST"])
def edit_todo_title(todo_id, todo_list_id):
    title = request.form.get("title")
    todo = Todo.get(todo_id)
    todo.set_title(title)
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/toggle_completed", methods=["GET"])
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
