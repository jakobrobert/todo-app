from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

import configparser
import datetime

from logic.long_term_todo_overview import LongTermTodoOverview
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

    setting_key = "sort_todo_lists_by"
    sort_by = __get_sort_by(setting_key)
    ascending_or_descending = __get_ascending_or_descending(setting_key)

    return render_template("todo_lists.html", todo_lists=todo_lists,
                           sort_by=sort_by, ascending_or_descending=ascending_or_descending)


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


@app.route(URL_PREFIX + "/long_term_todos/<int:id>/duration-chart", methods=["GET"])
def get_long_term_todo_duration_chart(id):
    long_term_todo = LongTermTodo.get(id)
    todos = Todo.get_all_of_long_term_todo(long_term_todo_id=id)
    labels, values = __get_labels_and_values_for_duration_chart(todos)

    return render_template("long_term_todo_duration_chart.html",
                           title=long_term_todo.title, total_duration=long_term_todo.duration,
                           labels=labels, values=values)


@app.route(URL_PREFIX + "/long_term_todos/<int:id>/progress-overview", methods=["GET"])
def get_long_term_todo_progress_overview(id):
    as_percents_arg = request.args.get("as_percents")
    as_percents = False
    if as_percents_arg == 'True':
        as_percents = True

    long_term_todo = LongTermTodo.get(id)
    todos = Todo.get_all_of_long_term_todo(long_term_todo_id=id)
    progress_goal = long_term_todo.progress_goal
    labels, values = __get_labels_and_values_for_progress_chart(todos, progress_goal, as_percents)
    table_data = __get_data_for_progress_overview(todos, progress_goal)

    return render_template(
        "long_term_todo_progress_overview.html",
        long_term_todo=long_term_todo, as_percents=as_percents, todos=todos,
        labels=labels, values=values, table_data=table_data)


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


def __get_labels_and_values_for_duration_chart(todos):
    labels = []
    values = []

    if not todos:
        return labels, values

    all_dates = __collect_dates_of_todos(todos)
    if not all_dates:
        return labels, values

    # Iterate through the each day and fill the data for the chart
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

    return labels, values


def __get_labels_and_values_for_progress_chart(todos, progress_goal, as_percents):
    labels = []
    values = []

    if not todos:
        return labels, values

    all_dates = __collect_dates_of_todos(todos)
    if not all_dates:
        return labels, values

    # Iterate through each day and fill the data for the chart
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
            # There is no valid progress value for the current date, so fill the value with the previous one
            if len(values) >= 1:
                values.append(values[-1])
            else:
                values.append(0)
        else:
            value = progress
            if as_percents:
                value = Utils.calculate_progress_in_percents(progress, progress_goal)

            values.append(value)

        curr_date += one_day

    return labels, values


def __get_data_for_progress_overview(todos, progress_goal):
    result = []

    if not todos:
        return result

    all_dates = __collect_dates_of_todos(todos)
    if not all_dates:
        return result

    # Iterate through each day & fill the data
    one_day = datetime.timedelta(days=1)
    curr_date = min(all_dates)
    end_date = max(all_dates)
    while curr_date <= end_date:
        curr_item = {}

        curr_item["date"] = str(curr_date)
        curr_item["has_progress"] = False

        progress = 0
        todos_for_date = __find_todos_for_date(todos, curr_date)
        if todos_for_date:
            # Get maximum progress for the current date
            for todo in todos_for_date:
                if todo.progress is not None and todo.progress > progress:
                    progress = todo.progress

        if progress == 0:
            # There is no valid progress value for the current date, so fill the value with the last one
            if len(result) >= 1:
                curr_item["progress"] = result[-1]["progress"]
                curr_item["progress_in_percents"] = result[-1]["progress_in_percents"]
            else:
                curr_item["progress"] = 0
                curr_item["progress_in_percents"] = 0
        else:
            curr_item["has_progress"] = True
            curr_item["progress"] = progress
            curr_item["progress_in_percents"] = Utils.calculate_progress_in_percents(progress, progress_goal)

        result.append(curr_item)

        curr_date += one_day

    return result


def __collect_dates_of_todos(todos):
    return LongTermTodoOverview.collect_dates_of_todos(todos)


def __find_todos_for_date(todos, date):
    todos_for_date = []

    for todo in todos:
        if todo.timestamp_completed is None:
            continue

        todo_date = todo.timestamp_completed.date()
        if todo_date == date:
            todos_for_date.append(todo)

    return todos_for_date
