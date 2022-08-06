from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB


db = SQLAlchemy()


class Base(db.Model):
    __abstract__ = True

    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class Task(Base):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(UUID(as_uuid=True), index=True, nullable=True)
    task_name = db.Column(db.String(100), nullable=False)
    params = db.Column(JSONB)
    status = db.Column(db.String(20), nullable=False)  # use choices
    celery_status = db.Column(db.String(20), nullable=True)  # use choices

    def __repr__(self):
        return "<Task %r>" % self.task_id
