import os
class BaseConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
