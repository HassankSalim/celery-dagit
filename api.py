from flask import jsonify, request
from flask_restful import Resource, Api

from model import db
from model import Task as TaskModel

api = Api(prefix="/api")


class Task(Resource):
    def post(self):
        """
        DAG of task to be runned
        basic version
        {
            'task_name': 'task.add'
            'args': [1, 1]
            'kwargs': {}
        }
        """
        request_data = request.get_json()
        params = {
            "args": request_data.get("args", []),
            "kwargs": request_data.get("kwargs", {}),
        }
        task = TaskModel(
            task_name=request_data["task_name"], params=params, status="PENDING"
        )
        db.session.add(task)
        db.session.commit()
        # async_id = celery_app.send_task(request_data['task_name'], tuple(request_data.get('args', [])), request_data.get('kwargs', {}))
        # print(async_id)
        return {"message": "Task will be started"}, 200


class Health(Resource):
    def get(self):
        return jsonify(ping="pong")


api.add_resource(Task, "/task")
api.add_resource(Health, "/health")
