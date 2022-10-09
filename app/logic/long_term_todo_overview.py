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

    @staticmethod
    def find_todos_for_date(todos, date):
        todos_for_date = []

        for todo in todos:
            if todo.timestamp_completed is None:
                continue

            todo_date = todo.timestamp_completed.date()
            if todo_date == date:
                todos_for_date.append(todo)

        return todos_for_date

