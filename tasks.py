from time import sleep
from celery import Celery

app = Celery(broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")


@app.task
def add(x, y):
    sleep(60)
    return x + y
