import datetime

from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

import configparser

from utils import Utils
from logic.long_term_todo_overview import LongTermTodoOverview

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

    setting_key = "sort_todo_lists_by"
    sort_by = __get_sort_by(setting_key)
    ascending_or_descending = __get_ascending_or_descending(setting_key)
    # TODO remove the time part
    today = datetime.datetime.today()
    tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)

    return render_template(
        "todo_lists.html",
        todo_lists=todo_lists, sort_by=sort_by, ascending_or_descending=ascending_or_descending,
        today=today, tomorrow=tomorrow
    )


@app.route(URL_PREFIX + "/todo_lists/add", methods=["POST"])
def add_todo_list():
    title = request.form.get("title")
    TodoList.add(title)
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists/add-daily-todo-list", methods=["POST"])
def add_daily_todo_list():
    # TODO implement
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

    setting_key = "sort_todos_by"
    sort_by = __get_sort_by(setting_key)
    ascending_or_descending = __get_ascending_or_descending(setting_key)

    return render_template("todo_list.html", todo_list_id=id, title=title, todos=todos, long_term_todos=long_term_todos,
                           sort_by=sort_by, ascending_or_descending=ascending_or_descending)


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

    setting_key = "sort_long_term_todos_by"
    sort_by = __get_sort_by(setting_key)
    ascending_or_descending = __get_ascending_or_descending(setting_key)

    return render_template("long_term_todos.html", long_term_todos=long_term_todos,
                           sort_by=sort_by, ascending_or_descending=ascending_or_descending)


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


@app.route(URL_PREFIX + "/sort_todo_lists", methods=["POST"])
def sort_todo_lists():
    __handle_sort_request(setting_key="sort_todo_lists_by")
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/sort_todos/<int:todo_list_id>", methods=["POST"])
def sort_todos(todo_list_id):
    __handle_sort_request(setting_key="sort_todos_by")
    return redirect(url_for("get_todo_list", id=todo_list_id))


@app.route(URL_PREFIX + "/sort_long_term_todos", methods=["POST"])
def sort_long_term_todos():
    __handle_sort_request(setting_key="sort_long_term_todos_by")
    return redirect(url_for("get_long_term_todos"))


@app.route(URL_PREFIX + "/long_term_todos/<int:id>/duration-overview", methods=["GET"])
def get_long_term_todo_duration_overview(id):
    long_term_todo = LongTermTodo.get(id)
    todos = Todo.get_all_of_long_term_todo(long_term_todo_id=id)

    long_term_todo_overview = LongTermTodoOverview(todos, long_term_todo.progress, long_term_todo.progress_goal)
    labels, values = long_term_todo_overview.get_labels_and_values_for_duration_chart()
    table_data = long_term_todo_overview.get_duration_overview_items()

    return render_template(
        "long_term_todo_duration_overview.html",
        title=long_term_todo.title, total_duration=long_term_todo.duration,
        labels=labels, values=values, table_data=table_data
    )


@app.route(URL_PREFIX + "/long_term_todos/<int:id>/progress-overview", methods=["GET"])
def get_long_term_todo_progress_overview(id):
    as_percents_arg = request.args.get("as_percents")
    as_percents = False
    if as_percents_arg == "on":
        as_percents = True

    time_span_last_x_days_arg = request.args.get("time_span_last_x_days")
    time_span_last_x_days = None
    if time_span_last_x_days_arg is not None:
        time_span_last_x_days = int(time_span_last_x_days_arg)

    long_term_todo = LongTermTodo.get(id)
    todos = Todo.get_all_of_long_term_todo(long_term_todo_id=id)
    progress_goal = long_term_todo.progress_goal
    progress = long_term_todo.progress

    long_term_todo_overview = LongTermTodoOverview(todos, progress_goal, progress, time_span_last_x_days)
    labels, values = long_term_todo_overview.get_labels_and_values_for_progress_chart(as_percents)
    max_value = 100 if as_percents else long_term_todo.progress_goal
    table_data = long_term_todo_overview.get_progress_overview_items()
    average_daily_progress_all_days =\
        Utils.round_decimal(long_term_todo_overview.get_average_daily_progress_all_days())
    average_daily_progress_all_days_in_percents =\
        Utils.calculate_progress_in_percents(average_daily_progress_all_days, progress_goal)
    average_daily_progress_active_days =\
        Utils.round_decimal(long_term_todo_overview.get_average_daily_progress_active_days())
    average_daily_progress_active_days_in_percents =\
        Utils.calculate_progress_in_percents(average_daily_progress_active_days, progress_goal)
    estimated_days_until_completion =\
        Utils.round_decimal(long_term_todo_overview.calculate_estimated_days_until_completion())
    estimated_date_of_completion = long_term_todo_overview.calculate_estimated_date_of_completion()

    return render_template(
        "long_term_todo_progress_overview.html",
        long_term_todo=long_term_todo, todos=todos,
        as_percents=as_percents, time_span_last_x_days=time_span_last_x_days,
        labels=labels, values=values, max_value=max_value, table_data=table_data,
        average_daily_progress_all_days=average_daily_progress_all_days,
        average_daily_progress_all_days_in_percents=average_daily_progress_all_days_in_percents,
        average_daily_progress_active_days=average_daily_progress_active_days,
        average_daily_progress_active_days_in_percents=average_daily_progress_active_days_in_percents,
        estimated_days_until_completion=estimated_days_until_completion,
        estimated_date_of_completion=estimated_date_of_completion
    )


def __get_sort_by(setting_key):
    setting = Setting.get(key=setting_key)
    if setting is None or setting.value is None:
        return "none"

    split_index = setting.value.rindex("_")  # find the last underscore
    sort_by = setting.value[:split_index]  # take part of string before the last underscore

    return sort_by


def __get_ascending_or_descending(setting_key):
    setting = Setting.get(key=setting_key)
    if setting is None or setting.value is None:
        return "none"

    split_index = setting.value.rindex("_")  # find the last underscore
    ascending_or_descending = setting.value[split_index + 1:]  # take part of string after the last underscore

    return ascending_or_descending


def __handle_sort_request(setting_key):
    sort_by = request.form.get("sort_by")
    ascending_or_descending = request.form.get("ascending_or_descending")
    key = setting_key
    if sort_by == "none" or ascending_or_descending == "none":
        value = None
    else:
        value = f"{sort_by}_{ascending_or_descending}"
    Setting.set(key, value)
