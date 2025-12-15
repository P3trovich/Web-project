from celery import Celery
from celery.schedules import crontab

def create_celery_app():
    app = Celery(
        'email_tasks',
        broker='redis://redis:6379/0',
        backend='redis://redis:6379/0'
    )

    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="Europe/Moscow",
        enable_utc=True,
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        task_acks_on_failure_or_timeout=True,
        broker_transport_options={"visibility_timeout": 3600},
    )

    app.conf.beat_schedule = {
        "send-weekly-digest": {
            "task": "celery_.tasks.sunday_reminder_task",
            "schedule": crontab(hour=12, minute=0, day_of_week="sun"),
        }
    }
    
    return app