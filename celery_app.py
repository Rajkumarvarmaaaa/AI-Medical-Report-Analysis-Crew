from celery import Celery
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    'crew_worker',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['worker'] # Points to the file containing the tasks (worker.py)
)

celery_app.conf.update(
    task_track_started=True,
)