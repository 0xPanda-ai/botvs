# -*- coding: utf-8 -*-

from flask import Flask
import os
from flask.cli import load_dotenv
from app.extensions import db


def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object("app.configs.%s.Config" % object_name)
    db.init_app(app)
    return app
