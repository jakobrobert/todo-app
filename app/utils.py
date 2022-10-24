class Utils:
    @staticmethod
    def calculate_progress_in_percents(progress, progress_goal):
        progress_in_percents = 100.0 * progress / progress_goal
        return Utils.round_decimal(progress_in_percents)

    @staticmethod
    def round_decimal(value):
        return round(value, 1)
