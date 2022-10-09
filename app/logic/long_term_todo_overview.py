import datetime

# Pycharm shows error for this import and expects "app.utils", but this fails on the dev server.
from utils import Utils


class LongTermTodoOverview:
    def __init__(self, todos):
        self.todos = todos

    # TODO rename new methods
    def get_labels_and_values_for_duration_chart_NEW(self):
        labels = []
        values = []

        if not self.todos:
            return labels, values

        all_dates = self.__collect_dates_of_todos_NEW()
        if not all_dates:
            return labels, values

        # Iterate through the each day and fill the data for the chart
        one_day = datetime.timedelta(days=1)
        curr_date = min(all_dates)
        end_date = max(all_dates)
        while curr_date <= end_date:
            date_label = str(curr_date)
            labels.append(date_label)

            todos_for_date = self.__find_todos_for_date_NEW(curr_date)
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

    def get_labels_and_values_for_progress_chart_NEW(self, progress_goal, as_percents):
        labels = []
        values = []

        if not self.todos:
            return labels, values

        all_dates = self.__collect_dates_of_todos_NEW()
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
            todos_for_date = self.__find_todos_for_date_NEW(curr_date)
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

    def get_data_for_progress_overview_NEW(self, progress_goal):
        result = []

        if not self.todos:
            return result

        all_dates = self.__collect_dates_of_todos_NEW()
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
            todos_for_date = self.__find_todos_for_date_NEW(curr_date)
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

    def __collect_dates_of_todos_NEW(self):
        all_dates = []
        for todo in self.todos:
            if todo.timestamp_completed is None:
                continue

            curr_date = todo.timestamp_completed.date()
            all_dates.append(curr_date)
        return all_dates

    def __find_todos_for_date_NEW(self, date):
        todos_for_date = []
        for todo in self.todos:
            if todo.timestamp_completed is None:
                continue

            todo_date = todo.timestamp_completed.date()
            if todo_date == date:
                todos_for_date.append(todo)
        return todos_for_date

