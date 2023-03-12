class Utils:
    @staticmethod
    def convert_to_percents(value, max_value):
        # Check to prevent TypeError or ZeroDivisionError
        if not value or not max_value:
            return 0

        progress_in_percents = 100.0 * value / max_value
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
