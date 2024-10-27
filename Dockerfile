FROM python:3.10

ENV PYTHONUNBUFFERED=1

RUN pip install "poetry==1.7.1"

RUN mkdir /application
WORKDIR /application

COPY project/app/pyproject.toml /application

RUN poetry config virtualenvs.create false  \
    && poetry install --no-interaction --no-ansi

COPY project/app /application
ENV PYTHONPATH "/application"

COPY ./start_cmd/start_project /start_project
RUN sed -i 's/\r$//g' /start_project
RUN chmod +x /start_project

COPY ./start_cmd/start_celery_beat /start_celery_beat
RUN sed -i 's/\r$//g' /start_celery_beat
RUN chmod +x /start_celery_beat

COPY ./start_cmd/start_celery_worker /start_celery_worker
RUN sed -i 's/\r$//g' /start_celery_worker
RUN chmod +x /start_celery_worker
