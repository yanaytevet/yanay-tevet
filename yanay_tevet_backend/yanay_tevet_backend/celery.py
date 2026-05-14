import os
from typing import Any

from celery import Celery, Task

from kombu import Queue

from yanay_tevet_backend.logger import app_logger

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yanay_tevet_backend.settings')


app = Celery('yanay_tevet_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')


MAIN_QUEUE_NAME = 'main'
EMAILS_QUEUE_NAME = 'emails'

app.conf.task_default_queue = MAIN_QUEUE_NAME
app.conf.task_queues = (
    Queue(MAIN_QUEUE_NAME, routing_key=MAIN_QUEUE_NAME),
    Queue(EMAILS_QUEUE_NAME, routing_key=EMAILS_QUEUE_NAME),
)


app.autodiscover_tasks([
    'users.tasks.daily_cleaning.daily_cleaning',
])


class AsyncTask(Task):
    def run(self, *args, **kwargs) -> Any:
        pass

    def __call__(self, *args, **kwargs) -> Any:
        app_logger.setCeleryLogger(self.name)
        app_logger.logger.info(f'{self.name}: started running with args: {args}, kwargs: {kwargs}')
        res = self.run(*args, **kwargs)
        app_logger.logger.info(f'{self.name}: finished running')
        return res

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        exc_tb = einfo.traceback
        app_logger.logger.info(f'{self.name}: failed\n{exc_tb}')
        # from emails.emails_manager.admin_emails_manager import AdminEmailsManager
        # error_body = f'{args}<br>{kwargs}<br><br>{exc_tb}'
        # AdminEmailsManager().send_error_to_rnd_admins(str(exc), error_body)

    def _log_error(self, task, req, einfo):
        pass


app.conf.beat_schedule = {
    'daily_cleaning': {
        'task': 'users.tasks.daily_cleaning.daily_cleaning',
        'schedule': 60 * 60 * 24,
        'options': {'queue': MAIN_QUEUE_NAME}
    },
}
app.conf.timezone = 'UTC'
