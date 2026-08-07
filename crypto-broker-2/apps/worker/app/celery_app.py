import os
from celery import Celery

url = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("cryptobroker", broker=url, backend=url)
