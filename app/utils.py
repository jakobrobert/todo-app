class Utils:
    @staticmethod
    def calculate_progress_in_percents(progress, progress_goal):
        # TODO CLEANUP remove None checks here, should be no problem. and if it is, should be dealt with on caller side
        if progress is None or progress_goal is None:
            return None

        progress_in_percents = 100.0 * progress / progress_goal
        return Utils.round_decimal(progress_in_percents)

    @staticmethod
    def round_decimal(value):
        return round(value, 1)
