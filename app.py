import os
import logging

from config import config
from model import db
from api import api

from flask import Flask

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s]: {} %(levelname)s %(message)s".format(os.getpid()),
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    api.init_app(app)

    db.init_app(app)
    return app


app = create_app()
if __name__ == "__main__":
    app.run()
