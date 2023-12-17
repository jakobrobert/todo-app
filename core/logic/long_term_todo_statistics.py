import datetime

from core.utils import Utils


class LongTermTodoStatistics:
    # Need to pass values separately instead of passing long_term_todo as a whole, then would raise Import error
    # when trying to import long_term_todo in this file
    def __init__(self, long_term_todo, todos, time_span_last_x_days=None):
        self.long_term_todo = long_term_todo
        self.todos = todos

        if time_span_last_x_days is None:
            self.time_span_last_x_days = None
        else:
            self.time_span_last_x_days = datetime.timedelta(days=time_span_last_x_days)

        self.date_and_todos_mapping_for_time_span = []
        self.statistics_items_for_time_span = []
        self.progress_for_last_day_before_time_span = 0

    def update_data(self):
        self.update_date_and_todos_mapping()
        self.update_statistics_items()
        self.update_progress_for_last_day_before_time_span()

    def update_date_and_todos_mapping(self):
        self.date_and_todos_mapping_for_time_span = []

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

            self.date_and_todos_mapping_for_time_span.append(curr_item)
            curr_date += one_day

    def update_statistics_items(self):
        self.statistics_items_for_time_span = []

        # TODONOW remove checks?
        if not self.todos:
            return

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return

        for date_and_todos_item in self.date_and_todos_mapping_for_time_span:
            statistics_item = self.__create_statistics_item(date_and_todos_item, self.statistics_items_for_time_span)
            self.statistics_items_for_time_span.append(statistics_item)

    def update_progress_for_last_day_before_time_span(self):
        self.progress_for_last_day_before_time_span = 0

        if not self.time_span_last_x_days:
            return

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return

        end_date = all_dates[-1]
        start_date = end_date - self.time_span_last_x_days
        date_one_day_before_start = start_date - datetime.timedelta(days=1)
        print(f"start_date: {start_date}, date_one_day_before_start: {date_one_day_before_start}")
        # TODONOW fix: need to find the last todo until this date
        todos_for_one_day_before_start = self.__find_todos_for_date(date_one_day_before_start)
        print(f"len(todos_for_one_day_before_start): {len(todos_for_one_day_before_start)}") # -> this is 0 as expected
        self.progress_for_last_day_before_time_span = self.__get_last_progress_of_todos(todos_for_one_day_before_start)

    def get_statistics_items(self):
        return self.statistics_items_for_time_span

    def get_total_duration_delta_as_hours(self):
        # Excluding the first date here because first date is excluded for progress_delta as well.
        # Would be more intuitive for full time span that first date is included for progress_delta
        #   but this might be trickier and need some adjustments of date_and_todos_mapping
        total_duration_delta_as_hours = 0
        date_and_todos_mapping_without_first_date = self.date_and_todos_mapping_for_time_span[1:]

        for date_and_todos_mapping_item in date_and_todos_mapping_without_first_date:
            curr_todos = date_and_todos_mapping_item["todos"]
            curr_todos_duration = self.__get_total_duration_for_todos(curr_todos)
            curr_todos_duration_as_hours = curr_todos_duration.total_seconds() / 3600
            total_duration_delta_as_hours += curr_todos_duration_as_hours

        return total_duration_delta_as_hours

    def get_all_days_count(self):
        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        if not self.date_and_todos_mapping_for_time_span:
            return 0

        filtered_dates = self.__filter_dates_by_time_span(all_dates)
        return LongTermTodoStatistics.__count_days(filtered_dates)

    def get_active_days_count(self):
        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        return self.__get_active_days_count_by_date_and_todos_mapping()

    def get_remaining_progress(self):
        if not self.long_term_todo.progress_goal or not self.long_term_todo.progress:
            return 0

        return self.long_term_todo.progress_goal - self.long_term_todo.progress

    # TODOLATER find occurrences of progress_delta, re-use this method there
    def get_progress_delta(self):
        if not self.date_and_todos_mapping_for_time_span:
            return 0

        todos_of_first_date = self.date_and_todos_mapping_for_time_span[0]["todos"]
        progress_of_first_date = self.__get_last_progress_of_todos(todos_of_first_date)

        return self.long_term_todo.progress - progress_of_first_date

    def get_estimated_remaining_days_until_completion(self):
        if not self.long_term_todo.progress or not self.long_term_todo.progress:
            return 0

        average_daily_progress = self.get_average_daily_progress_all_days()
        if average_daily_progress == 0:
            return 0

        return self.get_remaining_progress() / average_daily_progress

    def get_estimated_completion_date(self):
        days_until_completion = self.get_estimated_remaining_days_until_completion()
        if not days_until_completion:
            return None

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
        if not self.long_term_todo.progress:
            return 0

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        if not self.date_and_todos_mapping_for_time_span:
            return 0

        filtered_dates = self.__filter_dates_by_time_span(all_dates)
        all_days_count = LongTermTodoStatistics.__count_days(filtered_dates)
        # TODOLATER can simplify? use date_and_todos_mapping, is already filtered
        if all_days_count <= 1:
            return 0

        todos_of_first_date = self.date_and_todos_mapping_for_time_span[0]["todos"]
        start_progress = self.__get_last_progress_of_todos(todos_of_first_date)
        progress_delta = self.long_term_todo.progress - start_progress

        # Subtract 1 because progress_delta excludes the first date. Compare with get_average_progress_per_hour.
        return progress_delta / (all_days_count - 1)

    def get_average_daily_progress_active_days(self):
        if not self.long_term_todo.progress:
            return 0

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        if not self.date_and_todos_mapping_for_time_span:
            return 0

        active_days_count = self.__get_active_days_count_by_date_and_todos_mapping()
        if active_days_count <= 1:
            return 0

        todos_of_first_date = self.date_and_todos_mapping_for_time_span[0]["todos"]
        start_progress = self.__get_last_progress_of_todos(todos_of_first_date)
        progress_delta = self.long_term_todo.progress - start_progress

        # Subtract 1 because progress_delta excludes the first date. Compare with get_average_progress_per_hour.
        return progress_delta / (active_days_count - 1)

    def get_average_progress_per_hour(self):
        if not self.long_term_todo.progress:
            return 0

        # TODOLATER Remove unused code, see similar occurrences
        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        if not self.date_and_todos_mapping_for_time_span:
            return 0

        total_duration_delta_as_hours = self.get_total_duration_delta_as_hours()
        if total_duration_delta_as_hours == 0:
            return 0

        todos_of_first_date = self.date_and_todos_mapping_for_time_span[0]["todos"]
        start_progress = self.__get_last_progress_of_todos(todos_of_first_date)
        progress_delta = self.long_term_todo.progress - start_progress

        return progress_delta / total_duration_delta_as_hours

    def get_estimated_remaining_duration_until_completion(self):
        average_progress_per_hour = self.get_average_progress_per_hour()
        if not average_progress_per_hour:
            return None

        estimated_duration_as_hours = self.get_remaining_progress() / average_progress_per_hour
        return datetime.timedelta(hours=estimated_duration_as_hours)

    def get_estimated_total_duration_at_completion(self):
        estimated_remaining_duration = self.get_estimated_remaining_duration_until_completion()
        if not estimated_remaining_duration:
            return None

        estimated_total_duration = self.long_term_todo.total_duration + estimated_remaining_duration
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
        progress_goal = self.long_term_todo.progress_goal
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
        curr_item["progress_as_percents"] = Utils.convert_to_percents(progress, progress_goal)

        daily_progress = progress
        if prev_item is not None:
            daily_progress -= prev_item["progress"]
        else:
            daily_progress -= self.progress_for_last_day_before_time_span

        curr_item["daily_progress"] = daily_progress
        curr_item["daily_progress_as_percents"] = Utils.convert_to_percents(daily_progress, progress_goal)

    def __get_active_days_count_by_date_and_todos_mapping(self):
        if not self.date_and_todos_mapping_for_time_span:
            return 0

        active_days_count = 0

        for date_and_todos_item in self.date_and_todos_mapping_for_time_span:
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
