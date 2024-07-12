from celery import Celery

celery_app = Celery(
    'tasks',
    broker='amqp://myuser:mypassword@rabbitmq:5672/vhost',
    backend='rpc://'
)

celery_app.conf.beat_schedule = {
    'refresh_function': {
        'task': 'src.tasks.refresh_function',
        'schedule': 60.0,
    },
}

celery_app.conf.timezone = 'UTC'
