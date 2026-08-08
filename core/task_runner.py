import threading


class TaskRunner:
    """
    Runs long-running tasks in background threads
    so the UI remains responsive.
    """

    @staticmethod
    def run(task, on_success=None, on_error=None):
        def worker():
            try:
                result = task()

                if on_success:
                    on_success(result)

            except Exception as e:
                if on_error:
                    on_error(e)

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    @staticmethod
    def run_simple(task):
        """
        Run a task in a background thread without
        success/error callbacks (for streaming tasks
        that handle their own callbacks).
        """

        threading.Thread(
            target=task,
            daemon=True
        ).start()