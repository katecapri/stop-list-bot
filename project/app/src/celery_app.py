from celery import Celery
from kombu import Queue, Exchange, binding


app = Celery('default', include=['src.tasks'])

app.config_from_object('src.settings.celery_settings')

exchange = Exchange('default', type='direct')
app.conf.update(
    task_queues=(
        Queue('stop_lists', [binding(exchange, routing_key='stop_lists')]),
    )
)

app.conf.beat_schedule = {
    'tasks-inspector': {
        'task': 'src.tasks.save_stop_lists_for_restaurants_task',
        'schedule': 10800.0,
    },
}
