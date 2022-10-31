import datetime

# Pycharm shows error for this import and expects "app.utils", but this fails on the dev server.
from utils import Utils


class LongTermTodoOverview:
    # Need to pass values separately instead of passing long_term_todo as a whole, then raises Import error:
    # File ".../todo-app/dev/app/models/long_term_todo.py", line 1, in <module>
    #     from todo_app import db
    # ImportError: cannot import- name 'db'
    def __init__(self, todos, progress_goal, progress):
        self.todos = todos
        self.progress_goal = progress_goal
        self.progress = progress

    def get_labels_and_values_for_duration_chart(self):
        labels = []
        values = []

        if not self.todos:
            return labels, values

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return labels, values

        todos_by_date = self.__get_date_and_todos_mapping(all_dates)
        for item in todos_by_date:
            labels.append(item["date"])
            duration_in_minutes = LongTermTodoOverview.__get_total_duration_in_minutes_for_todos(item["todos"])
            values.append(duration_in_minutes)

        return labels, values

    def get_labels_and_values_for_progress_chart(self, as_percents):
        labels = []
        values = []

        data_items = self.get_progress_overview_items()
        if not data_items:
            return labels, values

        for item in data_items:
            labels.append(item["date"])

            if as_percents:
                values.append(item["progress_in_percents"])
            else:
                values.append(item["progress"])

        return labels, values

    def get_progress_overview_items(self):
        progress_items = []

        if not self.todos:
            return progress_items

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return progress_items

        date_and_todos_mapping = self.__get_date_and_todos_mapping(all_dates)
        for date_and_todos_item in date_and_todos_mapping:
            curr_progress_item = {
                "date": date_and_todos_item["date"],
                "is_active_day": False
            }

            for todo in date_and_todos_item["todos"]:
                if todo.completed:
                    curr_progress_item["is_active_day"] = True

            progress = self.__get_max_progress_for_todos(date_and_todos_item["todos"])

            prev_progress_item = progress_items[-1] if len(progress_items) >= 1 else None
            LongTermTodoOverview.__fill_item_for_progress_overview(
                curr_progress_item, prev_progress_item, progress, self.progress_goal
            )

            progress_items.append(curr_progress_item)

        return progress_items

    def get_average_daily_progress_all_days(self):
        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        all_days_count = LongTermTodoOverview.__count_days(all_dates)
        average_daily_progress = self.progress / all_days_count

        return Utils.round_decimal(average_daily_progress)

    def get_average_daily_progress_active_days(self):
        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        active_days_count = 0
        date_and_todos_mapping = self.__get_date_and_todos_mapping(all_dates)
        for date_and_todos_item in date_and_todos_mapping:
            todos = date_and_todos_item["todos"]
            for todo in todos:
                if todo.completed:
                    active_days_count += 1
                    break

        average_daily_progress = self.progress / active_days_count

        return Utils.round_decimal(average_daily_progress)

    def __collect_dates_of_todos(self):
        all_dates = []

        for todo in self.todos:
            if todo.timestamp_completed is None:
                continue

            curr_date = todo.timestamp_completed.date()
            all_dates.append(curr_date)

        return all_dates

    def __find_todos_for_date(self, date):
        todos_for_date = []

        for todo in self.todos:
            if todo.timestamp_completed is None:
                continue

            todo_date = todo.timestamp_completed.date()
            if todo_date == date:
                todos_for_date.append(todo)

        return todos_for_date

    def __get_date_and_todos_mapping(self, all_dates):
        result = []

        one_day = datetime.timedelta(days=1)
        curr_date = min(all_dates)
        end_date = max(all_dates)

        while curr_date <= end_date:
            curr_item = {
                "date": str(curr_date),
                "todos": self.__find_todos_for_date(curr_date)
            }

            result.append(curr_item)
            curr_date += one_day

        return result

    @staticmethod
    def __count_days(dates):
        start_date = min(dates)
        end_date = max(dates)
        time_span = end_date - start_date
        days = time_span.days + 1  # + 1 to count inclusively

        return days

    @staticmethod
    def __get_total_duration_in_minutes_for_todos(todos):
        if not todos:
            return 0

        total_duration_in_seconds = 0

        for todo in todos:
            if todo.duration is not None:
                total_duration_in_seconds += todo.duration.total_seconds()

        return total_duration_in_seconds / 60

    # TODO can change to get_last_progress, then just use value of last todo.
    @staticmethod
    def __get_max_progress_for_todos(todos):
        if not todos:
            return 0

        progress = 0

        for todo in todos:
            if todo.progress is not None and todo.progress > progress:
                progress = todo.progress

        return progress

    @staticmethod
    def __fill_item_for_progress_overview(curr_item, prev_item, progress, progress_goal):
        if progress == 0:
            curr_item["daily_progress"] = 0
            curr_item["daily_progress_in_percents"] = 0

            if prev_item is None:
                curr_item["progress"] = 0
                curr_item["progress_in_percents"] = 0

                return

            curr_item["progress"] = prev_item["progress"]
            curr_item["progress_in_percents"] = prev_item["progress_in_percents"]

            return

        curr_item["progress"] = progress
        curr_item["progress_in_percents"] = Utils.calculate_progress_in_percents(progress, progress_goal)

        relative_progress = progress
        if prev_item is not None:
            relative_progress -= prev_item["progress"]

        curr_item["daily_progress"] = relative_progress
        curr_item["daily_progress_in_percents"] = \
            Utils.calculate_progress_in_percents(relative_progress, progress_goal)
