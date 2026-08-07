from .celery_app import celery_app

@celery_app.task(name="app.tasks.health_check")
def health_check():
    return {"status": "ok"}
