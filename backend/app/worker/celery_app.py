from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

celery_app = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND","redis://127.0.0.1:6379/0")
)

#celery_app.config_from_object('worker.celeryconfig')
# refer to https://docs.celeryq.dev/en/stable/userguide/configuration.html
celery_app.conf.update(
    imports = ('worker.celery_worker',),
    broker_url = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0"),
    result_backend = os.getenv("CELERY_RESULT_BACKEND","redis://127.0.0.1:6379/0"),
    task_annotations = {'tasks.add': {'rate_limit': '10/s'}},
    task_queues = {
        'lazy-queue': {
            'exchange': 'lazy-queue',
        }
    },
    task_routes = {
        "worker.celery_worker.long_task": "lazy-queue",
        "worker.celery_worker.plan_task": "lazy-queue",
        "worker.celery_worker.exec_task": "lazy-queue"
    },
    # unit is seconds
    result_expires=600,
    task_acks_late=True,
    task_track_started = True,
    worker_concurrency = 4,
    worker_prefetch_multiplier = 4,
    worker_max_tasks_per_child = 10000
)