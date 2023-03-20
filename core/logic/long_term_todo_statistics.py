import datetime
from time import time

from core.utils import Utils


class LongTermTodoStatistics:
    # Need to pass values separately instead of passing long_term_todo as a whole, then would raise Import error
    # when trying to import long_term_todo in this file
    def __init__(self, todos, progress_goal, progress, time_span_last_x_days=None):
        self.todos = todos
        self.progress_goal = progress_goal
        self.progress = progress

        if time_span_last_x_days is None:
            self.time_span_last_x_days = None
        else:
            self.time_span_last_x_days = datetime.timedelta(days=time_span_last_x_days)

        self.date_and_todos_mapping = []
        self.statistics_items = []

    def update_data(self):
        self.update_date_and_todos_mapping()
        self.update_statistics_items()

    def update_date_and_todos_mapping(self):
        start_time = time()

        self.date_and_todos_mapping = []

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return

        filtered_dates = self.__filter_dates_by_time_span(all_dates)

        one_day = datetime.timedelta(days=1)
        curr_date = min(filtered_dates)
        end_date = max(filtered_dates)

        while curr_date <= end_date:
            curr_item = {
                "date": str(curr_date),
                "todos": self.__find_todos_for_date(curr_date)
            }

            self.date_and_todos_mapping.append(curr_item)
            curr_date += one_day

        end_time = time()
        elapsed_time_ms = 1000 * (end_time - start_time)
        print(f"LongTermTodo.update_date_and_todos_mapping => {elapsed_time_ms} ms")

    def update_statistics_items(self):
        start_time = time()

        self.statistics_items = []

        if not self.todos:
            end_time = time()
            elapsed_time_ms = 1000 * (end_time - start_time)
            print(f"LongTermTodo.update_statistics_items => {elapsed_time_ms} ms")
            return

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            end_time = time()
            elapsed_time_ms = 1000 * (end_time - start_time)
            print(f"LongTermTodo.update_statistics_items => {elapsed_time_ms} ms")
            return

        for date_and_todos_item in self.date_and_todos_mapping:
            self.statistics_items.append(self.__create_statistics_item(date_and_todos_item, self.statistics_items))

        end_time = time()
        elapsed_time_ms = 1000 * (end_time - start_time)
        print(f"LongTermTodo.update_statistics_items => {elapsed_time_ms} ms")

    def get_statistics_items(self):
        return self.statistics_items

    def get_all_days_count(self):
        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        if not self.date_and_todos_mapping:
            return 0

        filtered_dates = self.__filter_dates_by_time_span(all_dates)
        return LongTermTodoStatistics.__count_days(filtered_dates)

    def get_active_days_count(self):
        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        date_and_todos_mapping = self.date_and_todos_mapping

        return LongTermTodoStatistics.__get_active_days_count_by_date_and_todos_mapping(date_and_todos_mapping)

    def get_average_daily_duration_all_days(self):
        start_time = time()

        statistics_items = self.get_statistics_items()
        if not statistics_items:
            return datetime.timedelta(seconds=0)

        total_duration = datetime.timedelta(seconds=0)
        for item in statistics_items:
            total_duration += item["duration"]

        all_days_count = self.get_all_days_count()
        if all_days_count == 0:
            return total_duration

        result = total_duration / all_days_count

        end_time = time()
        elapsed_time_ms = 1000 * (end_time - start_time)
        print(f"LongTermTodo.get_average_daily_duration_all_days => {elapsed_time_ms} ms")

        return result

    def get_average_daily_duration_active_days(self):
        statistics_items = self.get_statistics_items()
        if not statistics_items:
            return datetime.timedelta(seconds=0)

        total_duration = datetime.timedelta(seconds=0)
        for item in statistics_items:
            total_duration += item["duration"]

        active_days_count = self.get_active_days_count()
        if active_days_count == 0:
            return datetime.timedelta(seconds=0)

        return total_duration / active_days_count

    def get_average_daily_progress_all_days(self):
        start_time = time()

        if not self.progress:
            return 0

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        if not self.date_and_todos_mapping:
            return 0

        # TODO also get rid of __filter_dates_by_time_span calls, integrate in update_data() ?
        filtered_dates = self.__filter_dates_by_time_span(all_dates)
        all_days_count = LongTermTodoStatistics.__count_days(filtered_dates)
        if all_days_count <= 1:
            return 0

        todos_of_first_date = self.date_and_todos_mapping[0]["todos"]
        start_progress = self.__get_last_progress_of_todos(todos_of_first_date)
        progress_delta = self.progress - start_progress

        # Subtract 1 as fix for #126
        result = progress_delta / (all_days_count - 1)

        end_time = time()
        elapsed_time_ms = 1000 * (end_time - start_time)
        print(f"LongTermTodo.get_average_daily_progress_all_days => {elapsed_time_ms} ms")

        return result

    def get_average_daily_progress_active_days(self):
        if not self.progress:
            return 0

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        if not self.date_and_todos_mapping:
            return 0

        # TODO simplify
        active_days_count = self.__get_active_days_count_by_date_and_todos_mapping(self.date_and_todos_mapping)
        if active_days_count <= 1:
            return 0

        todos_of_first_date = self.date_and_todos_mapping[0]["todos"]
        start_progress = self.__get_last_progress_of_todos(todos_of_first_date)
        progress_delta = self.progress - start_progress

        # Subtract 1 as fix for #126
        return progress_delta / (active_days_count - 1)

    def calculate_estimated_days_until_completion(self):
        if not self.progress or not self.progress:
            return 0

        remaining_progress = self.progress_goal - self.progress
        average_daily_progress = self.get_average_daily_progress_all_days()
        if average_daily_progress == 0:
            return 0

        return remaining_progress / average_daily_progress

    def calculate_estimated_date_of_completion(self):
        days_until_completion = self.calculate_estimated_days_until_completion()
        return datetime.date.today() + datetime.timedelta(days=days_until_completion)

    # TODO (remove this comment): The get_labels_and_values methods do not matter for performance, under 1 ms
    def get_labels_and_values_for_duration_chart(self):
        labels = []
        values = []

        statistics_items = self.get_statistics_items()
        if not statistics_items:
            return labels, values

        for item in statistics_items:
            date = item["date"]
            labels.append(date)
            duration = item["duration"]
            # Cannot use timedelta directly in chart, so pass as seconds.
            duration_as_seconds = duration.total_seconds()
            values.append(duration_as_seconds)

        return labels, values

    def get_labels_and_values_for_progress_chart(self, as_percents):
        labels = []
        values = []

        statistics_items = self.get_statistics_items()
        if not statistics_items:
            return labels, values

        for item in statistics_items:
            labels.append(item["date"])

            if as_percents:
                values.append(item["progress_as_percents"])
            else:
                values.append(item["progress"])

        return labels, values

    def __collect_dates_of_todos(self):
        all_dates = []

        for todo in self.todos:
            if todo.timestamp_completed is None:
                continue

            curr_date = todo.timestamp_completed.date()
            all_dates.append(curr_date)

        return all_dates

    def __filter_dates_by_time_span(self, dates):
        start_time = time()

        if not dates:
            return dates

        if not self.time_span_last_x_days:
            # time span is None or 0, so retain all dates
            return dates

        filtered_dates = []

        end_date = dates[-1]
        start_date = end_date - self.time_span_last_x_days

        for date in dates:
            if date >= start_date:
                filtered_dates.append(date)

        end_time = time()
        elapsed_time_ms = 1000 * (end_time - start_time)
        print(f"LongTermTodo.__filter_dates_by_time_span => {elapsed_time_ms} ms")

        return filtered_dates

    def __find_todos_for_date(self, date):
        todos_for_date = []

        for todo in self.todos:
            if todo.timestamp_completed is None:
                continue

            todo_date = todo.timestamp_completed.date()
            if todo_date == date:
                todos_for_date.append(todo)

        return todos_for_date

    def __create_statistics_item(self, date_and_todos_item, items):
        curr_item = {
            "date": date_and_todos_item["date"],
            "is_active_day": False
        }

        todos = date_and_todos_item["todos"]

        for todo in todos:
            if todo.completed:
                curr_item["is_active_day"] = True

        curr_item["duration"] = LongTermTodoStatistics.__get_total_duration_for_todos(todos)
        self.__add_progress_data_to_statistics_item(curr_item, items, todos)

        return curr_item

    def __add_progress_data_to_statistics_item(self, curr_item, items, todos):
        progress = self.__get_last_progress_of_todos(todos)
        prev_item = items[-1] if len(items) >= 1 else None

        if progress == 0:
            curr_item["daily_progress"] = 0
            curr_item["daily_progress_as_percents"] = 0

            if prev_item is None:
                curr_item["progress"] = 0
                curr_item["progress_as_percents"] = 0

                return

            curr_item["progress"] = prev_item["progress"]
            curr_item["progress_as_percents"] = prev_item["progress_as_percents"]

            return

        curr_item["progress"] = progress
        curr_item["progress_as_percents"] = Utils.convert_to_percents(progress, self.progress_goal)

        relative_progress = progress
        if prev_item is not None:
            relative_progress -= prev_item["progress"]

        curr_item["daily_progress"] = relative_progress
        curr_item["daily_progress_as_percents"] = Utils.convert_to_percents(relative_progress, self.progress_goal)

    @staticmethod
    def __get_active_days_count_by_date_and_todos_mapping(date_and_todos_mapping):
        if not date_and_todos_mapping:
            return 0

        active_days_count = 0

        for date_and_todos_item in date_and_todos_mapping:
            for todo in date_and_todos_item["todos"]:
                if todo.completed:
                    active_days_count += 1
                    break

        return active_days_count

    @staticmethod
    def __count_days(dates):
        start_date = min(dates)
        end_date = max(dates)
        time_span = end_date - start_date
        days = time_span.days + 1  # + 1 to count inclusively

        return days

    @staticmethod
    def __get_total_duration_for_todos(todos):
        if not todos:
            return datetime.timedelta(seconds=0)

        total_duration = datetime.timedelta(seconds=0)
        for todo in todos:
            if todo.duration is not None:
                total_duration += todo.duration

        return total_duration

    @staticmethod
    def __get_last_progress_of_todos(todos):
        if not todos:
            return 0

        progress = todos[-1].progress
        if progress is None:
            return 0

        return progress
