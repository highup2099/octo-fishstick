FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY app ./app
CMD ["celery", "-A", "app.celery_app.celery_app", "worker", "--loglevel=INFO"]
