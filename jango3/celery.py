import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jango3.settings')

app = Celery('jango3')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Тестовая задача для проверки работы Celery."""
    print(f'Request: {self.request!r}')
