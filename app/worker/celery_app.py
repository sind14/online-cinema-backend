from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "online_cinema",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"],
)

celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "delete_expired_tokens_every_hour": {
        "task": "app.worker.tasks.delete_expired_tokens",
        "schedule": crontab(minute=0),
    },
}
