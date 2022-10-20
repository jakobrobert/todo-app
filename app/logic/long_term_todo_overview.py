import datetime

# Pycharm shows error for this import and expects "app.utils", but this fails on the dev server.
from utils import Utils


class LongTermTodoOverview:
    def __init__(self, todos):
        self.todos = todos

    def get_labels_and_values_for_duration_chart(self):
        labels = []
        values = []

        if not self.todos:
            return labels, values

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return labels, values

        todos_by_date = self.__map_todos_to_dates(all_dates)
        for item in todos_by_date:
            labels.append(item["date"])
            duration_in_minutes = LongTermTodoOverview.__get_total_duration_in_minutes_for_todos(item["todos"])
            values.append(duration_in_minutes)

        return labels, values

    def get_labels_and_values_for_progress_chart(self, progress_goal, as_percents):
        labels = []
        values = []

        data_items = self.get_data_for_progress_overview(progress_goal)
        if not data_items:
            return labels, values

        for item in data_items:
            labels.append(item["date"])

            if as_percents:
                values.append(item["progress_in_percents"])
            else:
                values.append(item["progress"])

        return labels, values

    def get_data_for_progress_overview(self, progress_goal):
        result = []

        if not self.todos:
            return result

        all_dates = self.__collect_dates_of_todos()
        if not all_dates:
            return result

        todos_by_date = self.__map_todos_to_dates(all_dates)
        for item in todos_by_date:
            curr_item = {}

            curr_item["date"] = item["date"]
            curr_item["has_progress"] = False

            progress = self.__get_max_progress_for_todos(item["todos"])

            # TODO CLEANUP extract function, then can also use early returns instead of else
            # TODO add relative_progress_in_percents
            if progress == 0:
                curr_item["relative_progress"] = 0
                curr_item["relative_progress_in_percents"] = 0
                if len(result) >= 1:
                    # TODO CLEANUP extract var prev_item
                    curr_item["progress"] = result[-1]["progress"]
                    curr_item["progress_in_percents"] = result[-1]["progress_in_percents"]
                else:
                    curr_item["progress"] = 0
                    curr_item["progress_in_percents"] = 0
            else:
                curr_item["has_progress"] = True
                curr_item["progress"] = progress
                curr_item["progress_in_percents"] = Utils.calculate_progress_in_percents(progress, progress_goal)
                if len(result) >= 1:
                    relative_progress = progress - result[-1]["progress"]
                    curr_item["relative_progress"] = relative_progress
                    # TODO CLEANUP line too long, maybe will be fixed by "extract function"?
                    curr_item["relative_progress_in_percents"] = Utils.calculate_progress_in_percents(relative_progress, progress_goal)
                else:
                    curr_item["relative_progress"] = progress
                    curr_item["relative_progress_in_percents"] = Utils.calculate_progress_in_percents(progress, progress_goal)

            result.append(curr_item)

        return result

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

    def __map_todos_to_dates(self, all_dates):
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
    def __get_total_duration_in_minutes_for_todos(todos):
        if not todos:
            return 0

        total_duration_in_seconds = 0

        for todo in todos:
            if todo.duration is not None:
                total_duration_in_seconds += todo.duration.total_seconds()

        return total_duration_in_seconds / 60

    @staticmethod
    def __get_max_progress_for_todos(todos):
        if not todos:
            return 0

        progress = 0

        for todo in todos:
            if todo.progress is not None and todo.progress > progress:
                progress = todo.progress

        return progress
