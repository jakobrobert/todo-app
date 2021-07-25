from app import db
from app import app
from app import URL_PREFIX

from .models.todo import Todo
from .models.todo_list import TodoList
from .models.setting import Setting

from flask import render_template, request, redirect, url_for
from sqlalchemy import func


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
    """
    title = TodoList.query.filter_by(id=id).first().title
    query = Todo.query.filter_by(todo_list_id=id)
    order_by_clause = create_order_by_clause_for_todos()
    if order_by_clause is not None:
        query = query.order_by(order_by_clause)
    todos = query.all()
    """
    todo_list = TodoList.get(id=id)
    title = todo_list.title
    todos = todo_list.get_todos()
    return render_template("todo_list.html", todo_list_id=id, title=title, todos=todos)


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


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/toggle_priority", methods=["GET"])
def toggle_todo_priority(todo_id, todo_list_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.high_priority = not todo.high_priority
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
    Setting.set(key, value)
    return redirect(url_for("get_todo_list", id=todo_list_id))
