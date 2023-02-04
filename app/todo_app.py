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
    todo_lists = TodoList.get_all_sorted_using_setting()

    setting_key = "sort_todo_lists_by"
    sort_by = __get_sort_by(setting_key)
    ascending_or_descending = __get_ascending_or_descending(setting_key)

    date_format_string = "%a %Y-%m-%d"
    today_date = datetime.datetime.now().date()
    today_string = today_date.strftime(date_format_string)
    tomorrow_date = today_date + datetime.timedelta(days=1)
    tomorrow_string = tomorrow_date.strftime(date_format_string)

    return render_template(
        "todo_lists.html",
        todo_lists=todo_lists, sort_by=sort_by, ascending_or_descending=ascending_or_descending,
        today=today_string, tomorrow=tomorrow_string
    )


@app.route(URL_PREFIX + "/todo_lists/add", methods=["POST"])
def add_todo_list():
    title = request.form.get("title")
    TodoList.add(title)
    return redirect(url_for("get_todo_lists"))


@app.route(URL_PREFIX + "/todo_lists/add-daily-todo-list", methods=["POST"])
def add_daily_todo_list():
    day = request.form.get("day")
    TodoList.add(title=day)

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
    todos = Todo.get_all_of_todo_list_sorted_using_setting(todo_list_id=id)
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


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/timeline", methods=["GET"])
def get_todo_list_timeline(todo_list_id):
    todo_list = TodoList.get(todo_list_id)
    title = todo_list.title
    todos = Todo.get_all_of_todo_list(todo_list_id)

    todos = list(filter(lambda todo: todo.timestamp_completed is not None or todo.timestamp_started is not None, todos))
    todos.sort(key=__get_timestamp_of_todo_for_timeline)

    min_timestamp = datetime.datetime.max
    for todo in todos:
        if todo.timestamp_started is not None and todo.timestamp_started < min_timestamp:
            min_timestamp = todo.timestamp_started
        if todo.timestamp_completed is not None and todo.timestamp_completed < min_timestamp:
            min_timestamp = todo.timestamp_completed

    max_timestamp = datetime.datetime.min
    for todo in todos:
        if todo.timestamp_started is not None and todo.timestamp_started > max_timestamp:
            max_timestamp = todo.timestamp_started
        if todo.timestamp_completed is not None and todo.timestamp_completed > max_timestamp:
            max_timestamp = todo.timestamp_completed

    bar_items = []

    pixels_per_hour = 10
    fallback_width = 2
    curr_y = 0

    for todo in todos:
        bar_item = {"title": todo.title}

        if todo.timestamp_started is None:
            # No time tracking was done
            # -> For x position, use timestamp_completed & for width, use fallback
            time_delta = todo.timestamp_completed - min_timestamp
            time_delta_seconds = time_delta.total_seconds()
            time_delta_hours = time_delta_seconds / 3600
            bar_item["x"] = time_delta_hours * pixels_per_hour
            bar_item["width"] = fallback_width
        elif todo.timestamp_completed is None:
            # Time tracking has been started, but is not finished
            # -> For x position, use timestamp_started & for width, use fallback
            time_delta = todo.timestamp_started - min_timestamp
            time_delta_seconds = time_delta.total_seconds()
            time_delta_hours = time_delta_seconds / 3600
            bar_item["x"] = time_delta_hours * pixels_per_hour
            bar_item["width"] = fallback_width
        else:
            # Time tracking has been finished
            # -> For x position, use timestamp_started & for width, use the duration
            time_delta = todo.timestamp_started - min_timestamp
            time_delta_seconds = time_delta.total_seconds()
            time_delta_hours = time_delta_seconds / 3600
            bar_item["x"] = time_delta_hours * pixels_per_hour

            duration_time_delta = todo.timestamp_completed - todo.timestamp_started
            duration_time_delta_seconds = duration_time_delta.total_seconds()
            duration_time_delta_hours = duration_time_delta_seconds / 3600
            bar_item["width"] = duration_time_delta_hours * pixels_per_hour

        bar_item["y"] = curr_y
        bar_item["height"] = 25
        bar_items.append(bar_item)
        curr_y += 25

    return render_template("todo_list_timeline.html", title=title, bar_items=bar_items)


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


@app.route(URL_PREFIX + "/todo_lists/<int:todo_list_id>/todos/<int:todo_id>/edit-comment", methods=["POST"])
def edit_todo_comment(todo_id, todo_list_id):
    comment = request.form.get("comment")
    todo = Todo.get(todo_id)
    todo.set_comment(comment)
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
    todos = Todo.get_all_of_long_term_todo_sorted_using_setting(long_term_todo_id=id)
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
    todos = Todo.get_all_of_long_term_todo_sorted_using_setting(long_term_todo_id=id)
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
    todos = Todo.get_all_of_long_term_todo_sorted_using_setting(long_term_todo_id=id)

    long_term_todo_overview = LongTermTodoOverview(todos, long_term_todo.progress, long_term_todo.progress_goal)
    labels, values = long_term_todo_overview.get_labels_and_values_for_duration_chart()
    table_data = long_term_todo_overview.get_duration_overview_items()
    all_days_count = long_term_todo_overview.get_all_days_count()
    active_days_count = long_term_todo_overview.get_active_days_count()
    active_days_percents = Utils.calculate_progress_in_percents(active_days_count, all_days_count)
    average_daily_duration_all_days = Utils.convert_timedelta_to_string(
        long_term_todo_overview.get_average_daily_duration_all_days()
    )
    average_daily_duration_active_days = Utils.convert_timedelta_to_string(
        long_term_todo_overview.get_average_daily_duration_active_days()
    )

    return render_template(
        "long_term_todo_duration_overview.html",
        long_term_todo=long_term_todo,
        labels=labels, values=values, table_data=table_data,
        all_days_count=all_days_count, active_days_count=active_days_count, active_days_percents=active_days_percents,
        average_daily_duration_all_days=average_daily_duration_all_days,
        average_daily_duration_active_days=average_daily_duration_active_days
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
    todos = Todo.get_all_of_long_term_todo_sorted_using_setting(long_term_todo_id=id)
    progress_goal = long_term_todo.progress_goal
    progress = long_term_todo.progress

    long_term_todo_overview = LongTermTodoOverview(todos, progress_goal, progress, time_span_last_x_days)
    labels, values = long_term_todo_overview.get_labels_and_values_for_progress_chart(as_percents)

    max_value = 100 if as_percents else long_term_todo.progress_goal
    progress_overview_items = long_term_todo_overview.get_progress_overview_items()

    item_with_min_progress = min(progress_overview_items, key=lambda item: item["progress"])
    min_value = item_with_min_progress["progress_as_percents"] if as_percents else item_with_min_progress["progress"]

    all_days_count = long_term_todo_overview.get_all_days_count()
    active_days_count = long_term_todo_overview.get_active_days_count()
    # TODO CLEANUP name is misleading, rename, here has nothing to do with progress
    active_days_percents = Utils.calculate_progress_in_percents(active_days_count, all_days_count)

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
        labels=labels, values=values, min_value=min_value, max_value=max_value, table_data=progress_overview_items,
        all_days_count=all_days_count, active_days_count=active_days_count, active_days_percents=active_days_percents,
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


def __get_timestamp_of_todo_for_timeline(todo):
    if todo.timestamp_started is None and todo.timestamp_completed is None:
        return None

    if todo.timestamp_completed is None:
        return todo.timestamp_started

    return todo.timestamp_completed
