class Utils:
    @staticmethod
    def calculate_progress_in_percents(progress, progress_goal):
        if progress is None or progress_goal is None:
            return None
        # TODO split up to make more readable
        return round(100.0 * progress / progress_goal, 1)
