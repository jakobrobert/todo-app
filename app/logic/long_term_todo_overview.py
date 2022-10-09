class LongTermTodoOverview:
    @staticmethod
    def collect_dates_of_todos(todos):
        all_dates = []

        for todo in todos:
            if todo.timestamp_completed is None:
                continue

            curr_date = todo.timestamp_completed.date()
            all_dates.append(curr_date)

        return all_dates
