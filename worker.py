from threading import Thread
from time import sleep
from celery import Celery
from celery.states import READY_STATES
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from config import config
from model import Task


class CeleryEventReceiver(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.celery_app = Celery(
            broker=config.CELERY_BROKER,
        )
        self.state = self.celery_app.events.State()
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=True)
        self.Session = sessionmaker()
        self.Session.configure(bind=engine)

    def notify(self, event):
        event_type: str = event.get("type")
        if not event_type.startswith('task-'):
            # Since we are only exporting metrics related to celery task
            # worker event can be filtered out
            return
        try:
            event_details, event_type = self.state.event(event)
            event, _ = event_details
            session = self.Session()
            update_data = {Task.celery_status: event.state}
            if event.state in READY_STATES:
                update_data[Task.status] = 'COMPLETED'

            session.query(Task).filter_by(task_id=event.uuid).update(update_data)
            session.commit()
        except Exception as e:
            print(e)

    def run(self) -> None:
        with self.celery_app.connection() as connection:
            while True:
                try:
                    receiver = self.celery_app.events.Receiver(
                        connection, handlers={"*": self.notify}
                    )
                    receiver.capture(limit=None, timeout=120)
                except Exception:
                    sleep(10)


class CeleryTaskInitiator(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.celery_app = Celery(
            broker=config.CELERY_BROKER,
        )
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=True)
        self.Session = sessionmaker()
        self.Session.configure(bind=engine)

    @staticmethod
    def get_one_pending_task(session):
        return session.query(Task).filter_by(status='PENDING', celery_status=None).first()

    def run(self) -> None:
        while True:
            try:
                session = self.Session()
                task = self.get_one_pending_task(session)
                if not task:
                    sleep(10)
                    continue
                params = task.params or {}
                async_task = self.celery_app.send_task(task.task_name, **params)
                task.task_id = async_task.id
                task.status = 'IN PROGRESS'
                session.commit()
            except Exception as e:
                print(e)
                sleep(10)


if __name__ == "__main__":
    task_initiator = CeleryTaskInitiator()
    task_initiator.start()

    event_receiver = CeleryEventReceiver()
    event_receiver.run()
