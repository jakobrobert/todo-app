class Utils:
    # TODO Rename, is more general, nothing to do with progress
    @staticmethod
    def calculate_progress_in_percents(progress, progress_goal):
        # This check is needed, otherwise TypeError can occur
        if progress is None or progress_goal is None:
            return

        progress_in_percents = 100.0 * progress / progress_goal
        return Utils.round_decimal(progress_in_percents)

    @staticmethod
    def round_decimal(value):
        return round(value, 1)

    @staticmethod
    def convert_timedelta_to_string(timedelta):
        if timedelta is None:
            return "n/a"

        seconds_of_last_day = timedelta.seconds
        hours_of_last_day, remaining_seconds = divmod(seconds_of_last_day, 3600)
        minutes = remaining_seconds // 60
        total_hours = timedelta.days * 24 + hours_of_last_day
        formatted_string = f"{total_hours:02}:{minutes:02}"

        return formatted_string
