import logging.config


class AppLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def setCeleryLogger(self, task_full_name: str) -> None:
        task_name = task_full_name.split('.')[-1]

        from django.conf import settings
        settings.LOGGING['handlers']['file']['filename'] = f'{settings.LOGS_LOCATION}/celery_{task_name}.log'
        logging.config.dictConfig(settings.LOGGING)

        self.logger = logging.getLogger(__name__)


app_logger = AppLogger()
