from yanay_tevet_backend import celery
from yanay_tevet_backend.celery import AsyncTask


@celery.app.task(base=AsyncTask, queue=celery.MAIN_QUEUE_NAME)
def daily_cleaning() -> None:
    pass
