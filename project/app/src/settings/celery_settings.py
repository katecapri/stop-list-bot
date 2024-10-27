import os
import datetime


broker_url = os.getenv("CELERY_BROKER_URL")
result_backend = os.getenv("CELERY_RESULT_BACKEND")
broker_connection_retry_on_startup = bool(os.getenv("CELERY_BROKER_CONN_RETRY_ON_START"))
timezone = os.getenv("CELERY_TIMEZONE")
enable_utc = bool(os.getenv("CELERY_ENABLE_UTC"))
task_time_limit = os.getenv("CELERY_TASK_TIME_LIMIT")
result_expires = datetime.timedelta(hours=12)
