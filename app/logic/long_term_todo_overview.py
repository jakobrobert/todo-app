import datetime

# Pycharm shows error for this import and expects "app.utils", but this fails on the dev server.
from utils import Utils


class LongTermTodoOverview:
    # Need to pass values separately instead of passing long_term_todo as a whole, then raises Import error
    # when trying to import long_term_todo in this file
    def __init__(self, todos, progress_goal, progress, time_span_last_x_days=None):
        self.todos = todos
        self.progress_goal = progress_goal
        self.progress = progress
        if time_span_last_x_days is None:
            self.time_span_last_x_days = None
        else:
            self.time_span_last_x_days = datetime.timedelta(days=time_span_last_x_days)

    def get_labels_and_values_for_duration_chart(self):
        labels = []
        values = []

        duration_items = self.get_duration_overview_items()
        if not duration_items:
            return labels, values

        for item in duration_items:
            labels.append(item["date"])
            values.append(item["duration_in_minutes"])

        return labels, values

    def get_average_daily_duration_all_days(self):
        duration_items = self.get_duration_overview_items()
        if not duration_items:
            return 0

        total_duration = 0
        for item in duration_items:
            total_duration += item["duration_in_minutes"]

        print(f"total_duration: {total_duration}")

        # TODO CLEANUP can extract __get_all_days_count
        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        filtered_dates = self.__filter_dates(all_dates)
        date_and_todos_mapping = self.__get_date_and_todos_mapping(filtered_dates)
        if not date_and_todos_mapping:
            return 0

        all_days_count = LongTermTodoOverview.__count_days(filtered_dates)
        print(f"all_days_count: {all_days_count}")

        print(f"average_daily_duration_all_days {total_duration / all_days_count}")

        return total_duration / all_days_count

    def get_average_daily_duration_active_days(self):
        duration_items = self.get_duration_overview_items()
        if not duration_items:
            return 0

        total_duration = 0
        for item in duration_items:
            total_duration += item["duration_in_minutes"]

        print(f"total_duration: {total_duration}")

        active_days_count = self.__get_active_days_count()

        if active_days_count == 0:
            return 0

        print(f"average_daily_duration_active_days {total_duration / active_days_count}")

        return total_duration / active_days_count

    def get_labels_and_values_for_progress_chart(self, as_percents):
        labels = []
        values = []

        progress_items = self.get_progress_overview_items()
        if not progress_items:
            return labels, values

        for item in progress_items:
            labels.append(item["date"])

            if as_percents:
                values.append(item["progress_in_percents"])
            else:
                values.append(item["progress"])

        return labels, values

    def get_duration_overview_items(self):
        duration_items = []

        if not self.todos:
            return duration_items

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return duration_items

        date_and_todos_mapping = self.__get_date_and_todos_mapping(all_dates)
        for date_and_todos_item in date_and_todos_mapping:
            curr_duration_item = {
                "date": date_and_todos_item["date"],
                "is_active_day": False
            }

            todos = date_and_todos_item["todos"]
            for todo in todos:
                if todo.completed:
                    curr_duration_item["is_active_day"] = True

            duration_in_minutes = LongTermTodoOverview.__get_total_duration_in_minutes_for_todos(todos)
            curr_duration_item["duration_in_minutes"] = Utils.round_decimal(duration_in_minutes)

            duration_items.append(curr_duration_item)

        return duration_items

    def get_progress_overview_items(self):
        progress_items = []

        if not self.todos:
            return progress_items

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return progress_items

        filtered_dates = self.__filter_dates(all_dates)

        date_and_todos_mapping = self.__get_date_and_todos_mapping(filtered_dates)
        for date_and_todos_item in date_and_todos_mapping:
            curr_progress_item = {
                "date": date_and_todos_item["date"],
                "is_active_day": False
            }

            todos = date_and_todos_item["todos"]
            for todo in todos:
                if todo.completed:
                    curr_progress_item["is_active_day"] = True

            progress = self.__get_last_progress_of_todos(todos)

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

        filtered_dates = self.__filter_dates(all_dates)
        date_and_todos_mapping = self.__get_date_and_todos_mapping(filtered_dates)
        if not date_and_todos_mapping:
            return 0

        all_days_count = LongTermTodoOverview.__count_days(filtered_dates)

        todos_of_first_date = date_and_todos_mapping[0]["todos"]
        start_progress = self.__get_last_progress_of_todos(todos_of_first_date)
        progress_delta = self.progress - start_progress

        return progress_delta / all_days_count

    def get_average_daily_progress_active_days(self):
        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        filtered_dates = self.__filter_dates(all_dates)
        date_and_todos_mapping = self.__get_date_and_todos_mapping(filtered_dates)
        if not date_and_todos_mapping:
            return 0

        active_days_count = 0
        for date_and_todos_item in date_and_todos_mapping:
            todos = date_and_todos_item["todos"]
            for todo in todos:
                if todo.completed:
                    active_days_count += 1
                    break

        todos_of_first_date = date_and_todos_mapping[0]["todos"]
        start_progress = self.__get_last_progress_of_todos(todos_of_first_date)
        progress_delta = self.progress - start_progress

        return progress_delta / active_days_count

    def calculate_estimated_days_until_completion(self):
        remaining_progress = self.progress_goal - self.progress
        average_daily_progress = self.get_average_daily_progress_all_days()

        return remaining_progress / average_daily_progress

    def calculate_estimated_date_of_completion(self):
        days_until_completion = self.calculate_estimated_days_until_completion()
        return datetime.date.today() + datetime.timedelta(days=days_until_completion)

    def __collect_dates_of_todos(self):
        all_dates = []

        for todo in self.todos:
            if todo.timestamp_completed is None:
                continue

            curr_date = todo.timestamp_completed.date()
            all_dates.append(curr_date)

        return all_dates

    def __filter_dates(self, dates):
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

    def __get_active_days_count(self):
        active_days_count = 0

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return 0

        filtered_dates = self.__filter_dates(all_dates)
        date_and_todos_mapping = self.__get_date_and_todos_mapping(filtered_dates)

        if not date_and_todos_mapping:
            return 0

        for date_and_todos_item in date_and_todos_mapping:
            for todo in date_and_todos_item["todos"]:
                if todo.completed:
                    active_days_count += 1
                    break

        print(f"active_days_count: {active_days_count}")
        return active_days_count

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

    @staticmethod
    def __get_last_progress_of_todos(todos):
        if not todos:
            return 0

        progress = todos[-1].progress
        if progress is None:
            return 0

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
