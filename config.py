class DevConfig:
    FLASK_ENV = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://:@localhost/dagit"
    CELERY_BROKER = "redis://:@localhost:6379/0"

    def as_dict(self):
        res = {}
        for atr in [f for f in dir(self) if not "__" in f]:
            val = getattr(self, atr)
            res[atr] = val
        return res


config = DevConfig()
