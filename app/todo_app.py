from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

import configparser
import datetime

from utils import Utils

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
    high_priority = request.form.get("high_priority") == "on"
    Todo.add(title, high_priority, todo_list_id)
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/add-by-long-term-todo", methods=["POST"])
def add_todo_by_long_term_todo(todo_list_id):
    long_term_todo_id = request.form.get("long_term_todo_id")
    high_priority = request.form.get("high_priority") == "on"
    long_term_todo = LongTermTodo.get(long_term_todo_id)
    long_term_todo.add_todo(high_priority, todo_list_id)
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


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/edit_progress", methods=["POST"])
def edit_todo_progress(todo_id, todo_list_id):
    progress = request.form.get("progress")
    todo = Todo.get(todo_id)
    todo.set_progress(progress)
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/start", methods=["GET"])
def start_todo(todo_id, todo_list_id):
    todo = Todo.get(todo_id)
    todo.start()
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/stop", methods=["GET"])
def stop_todo(todo_id, todo_list_id):
    todo = Todo.get(todo_id)
    todo.stop()
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
    todos = Todo.get_all_of_long_term_todo(long_term_todo_id=id)
    return render_template("long_term_todo.html", long_term_todo=long_term_todo, todos=todos)


@app.route(URL_PREFIX + "/long_term_todos/add", methods=["POST"])
def add_long_term_todo():
    title = request.form.get("title")
    progress_goal = request.form.get("progress_goal")
    LongTermTodo.add(title, progress_goal)
    return redirect(url_for("get_long_term_todos"))


@app.route(URL_PREFIX + "/long_term_todos/<int:id>/edit-title", methods=["POST"])
def edit_long_term_todo_title(id):
    title = request.form.get("title")
    long_term_todo = LongTermTodo.get(id)
    long_term_todo.set_title(title)
    return redirect(url_for("get_long_term_todos"))


@app.route(URL_PREFIX + "/long_term_todos/<int:id>/edit-progress-goal", methods=["POST"])
def edit_long_term_todo_progress_goal(id):
    progress_goal = request.form.get("progress_goal")
    long_term_todo = LongTermTodo.get(id)
    long_term_todo.set_progress_goal(progress_goal)
    todos = Todo.get_all_of_long_term_todo(long_term_todo_id=id)
    for todo in todos:
        todo.set_progress_goal(progress_goal)
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


@app.route(URL_PREFIX + "/long_term_todos/<int:id>/duration-chart", methods=["GET"])
def get_long_term_todo_duration_chart(id):
    long_term_todo = LongTermTodo.get(id)
    todos = Todo.get_all_of_long_term_todo(long_term_todo_id=id)

    all_dates = __collect_dates_of_todos(todos)

    # Iterate through the each day and fill the data for the chart
    labels = []
    values = []
    one_day = datetime.timedelta(days=1)
    curr_date = min(all_dates)
    end_date = max(all_dates)
    while curr_date <= end_date:
        date_label = str(curr_date)
        labels.append(date_label)

        todos_for_date = __find_todos_for_date(todos, curr_date)
        if todos_for_date:
            # Fill value with total duration for the current date
            duration_in_seconds = 0
            for todo in todos_for_date:
                if todo.duration is not None:
                    duration_in_seconds += todo.duration.total_seconds()

            duration_in_minutes = duration_in_seconds / 60
            values.append(duration_in_minutes)
        else:
            # There is no to-do for the current date, so fill the value with 0
            values.append(0)

        curr_date += one_day

    return render_template("long_term_todo_duration_chart.html",
                           title=long_term_todo.title, total_duration=long_term_todo.duration,
                           labels=labels, values=values)


@app.route(URL_PREFIX + "/long_term_todos/<int:id>/progress-chart", methods=["GET"])
def get_long_term_todo_progress_chart(id):
    as_percents_arg = request.args.get("as_percents")
    as_percents = False
    if as_percents_arg == 'True':
        as_percents = True

    long_term_todo = LongTermTodo.get(id)
    todos = Todo.get_all_of_long_term_todo(long_term_todo_id=id)

    all_dates = __collect_dates_of_todos(todos)

    # Iterate through the each day and fill the data for the chart
    labels = []
    values = []
    one_day = datetime.timedelta(days=1)
    curr_date = min(all_dates)
    end_date = max(all_dates)
    while curr_date <= end_date:
        date_label = str(curr_date)
        labels.append(date_label)

        progress = 0
        todos_for_date = __find_todos_for_date(todos, curr_date)
        if todos_for_date:
            # Get maximum progress for the current date
            for todo in todos_for_date:
                if todo.progress is not None and todo.progress > progress:
                    progress = todo.progress

        if progress == 0:
            # There is no valid value for the current date, so fill the value with the last one
            if len(values) >= 1:
                values.append(values[-1])
            else:
                values.append(0)
        else:
            value = progress
            if as_percents:
                value = Utils.calculate_progress_in_percents(progress, long_term_todo.progress_goal)

            values.append(value)

        curr_date += one_day

    return render_template("long_term_todo_progress_chart.html",
                           long_term_todo=long_term_todo, as_percents=as_percents, labels=labels, values=values)


def __collect_dates_of_todos(todos):
    all_dates = []

    for todo in todos:
        if todo.timestamp_completed is None:
            continue

        curr_date = todo.timestamp_completed.date()
        all_dates.append(curr_date)

    return all_dates


def __find_todos_for_date(todos, date):
    todos_for_date = []

    for todo in todos:
        if todo.timestamp_completed is None:
            continue

        todo_date = todo.timestamp_completed.date()
        if todo_date == date:
            todos_for_date.append(todo)

    return todos_for_date
