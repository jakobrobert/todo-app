import datetime

from core.utils import Utils


class LongTermTodoStatistics:
    # Need to pass values separately instead of passing long_term_todo as a whole, then would raise Import error
    # when trying to import long_term_todo in this file
    def __init__(self, long_term_todo, todos, progress_goal, progress, total_duration, time_span_last_x_days=None):
        self.todos = todos
        self.progress_goal = progress_goal
        self.progress = progress
        self.total_duration = total_duration
        self.long_term_todo = long_term_todo
        print(f"total_duration: {long_term_todo.total_duration}") # TODONOW remove

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

    def update_statistics_items(self):
        self.statistics_items = []

        if not self.todos:
            return

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return

        for date_and_todos_item in self.date_and_todos_mapping:
            self.statistics_items.append(self.__create_statistics_item(date_and_todos_item, self.statistics_items))

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

        return self.__get_active_days_count_by_date_and_todos_mapping()

    def get_remaining_progress(self):
        return self.progress_goal - self.progress

    def get_estimated_days_until_completion(self):
        if not self.progress or not self.progress:
            return 0

        average_daily_progress = self.get_average_daily_progress_all_days()
        if average_daily_progress == 0:
            return 0

        return self.get_remaining_progress() / average_daily_progress

    def get_estimated_date_of_completion(self):
        days_until_completion = self.get_estimated_days_until_completion()
        return datetime.date.today() + datetime.timedelta(days=days_until_completion)

    def get_average_daily_duration_all_days(self):
        statistics_items = self.get_statistics_items()
        if not statistics_items:
            return datetime.timedelta(seconds=0)

        total_duration = datetime.timedelta(seconds=0)
        for item in statistics_items:
            total_duration += item["duration"]

        all_days_count = self.get_all_days_count()
        if all_days_count == 0:
            return total_duration

        return total_duration / all_days_count

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
        if not self.progress:
            return 0

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        if not self.date_and_todos_mapping:
            return 0

        filtered_dates = self.__filter_dates_by_time_span(all_dates)
        all_days_count = LongTermTodoStatistics.__count_days(filtered_dates)
        if all_days_count <= 1:
            return 0

        todos_of_first_date = self.date_and_todos_mapping[0]["todos"]
        start_progress = self.__get_last_progress_of_todos(todos_of_first_date)
        progress_delta = self.progress - start_progress

        # Subtract 1 as fix for #126
        return progress_delta / (all_days_count - 1)

    def get_average_daily_progress_active_days(self):
        if not self.progress:
            return 0

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        if not self.date_and_todos_mapping:
            return 0

        active_days_count = self.__get_active_days_count_by_date_and_todos_mapping()
        if active_days_count <= 1:
            return 0

        todos_of_first_date = self.date_and_todos_mapping[0]["todos"]
        start_progress = self.__get_last_progress_of_todos(todos_of_first_date)
        progress_delta = self.progress - start_progress

        # Subtract 1 as fix for #126
        return progress_delta / (active_days_count - 1)

    def get_average_progress_per_hour(self):
        if not self.progress:
            return 0

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        if not self.date_and_todos_mapping:
            return 0

        total_duration_as_hours = 0
        for date_and_todos_mapping_item in self.date_and_todos_mapping:
            curr_todos = date_and_todos_mapping_item["todos"]
            curr_todos_duration = self.__get_total_duration_for_todos(curr_todos)
            curr_todos_duration_as_hours = curr_todos_duration.total_seconds() / 3600
            total_duration_as_hours += curr_todos_duration_as_hours

        if total_duration_as_hours == 0:
            return 0

        todos_of_first_date = self.date_and_todos_mapping[0]["todos"]
        start_progress = self.__get_last_progress_of_todos(todos_of_first_date)
        progress_delta = self.progress - start_progress

        return progress_delta / total_duration_as_hours

    def get_estimated_remaining_duration_until_completion(self):
        average_progress_per_hour = self.get_average_progress_per_hour()
        if average_progress_per_hour == 0:
            return None

        estimated_duration_as_hours = self.get_remaining_progress() / average_progress_per_hour
        return datetime.timedelta(hours=estimated_duration_as_hours)

    def get_estimated_total_duration_at_completion(self):
        estimated_remaining_duration = self.get_estimated_remaining_duration_until_completion()
        estimated_total_duration = self.total_duration + estimated_remaining_duration
        return estimated_total_duration

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

    def get_labels_and_values_for_daily_progress_chart(self, as_percents):
        labels = []
        values = []

        statistics_items = self.get_statistics_items()
        if not statistics_items:
            return labels, values

        for item in statistics_items:
            labels.append(item["date"])

            if as_percents:
                values.append(item["daily_progress_as_percents"])
            else:
                values.append(item["daily_progress"])

        return labels, values

    def get_labels_and_values_for_daily_progress_per_hour_chart(self):
        labels = []
        values = []

        statistics_items = self.get_statistics_items()
        if not statistics_items:
            return labels, values

        for item in statistics_items:
            labels.append(item["date"])
            values.append(item["daily_progress_per_hour"])

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

        if curr_item["duration"] and curr_item["daily_progress"]:
            duration_as_hours = curr_item["duration"].total_seconds() / 3600
            curr_item["daily_progress_per_hour"] = curr_item["daily_progress"] / duration_as_hours
        else:
            curr_item["daily_progress_per_hour"] = 0

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

    def __get_active_days_count_by_date_and_todos_mapping(self):
        if not self.date_and_todos_mapping:
            return 0

        active_days_count = 0

        for date_and_todos_item in self.date_and_todos_mapping:
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

        for todo in reversed(todos):
            if todo.completed:
                return todo.progress or 0

        return 0
