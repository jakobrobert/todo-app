class Utils:
    @staticmethod
    def calculate_progress_in_percents(progress, progress_goal):
        if progress is None or progress_goal is None:
            return None
        progress_in_percents = 100.0 * progress / progress_goal
        progress_in_percents_rounded = round(progress_in_percents, 1)
        return progress_in_percents_rounded
