__author__ = "Stefan"

from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy as FlaskSQLAlchemy

cors = CORS(reseources={r"/public/*": {"origins": "*"}})

db = FlaskSQLAlchemy()
ma = Marshmallow()

flask_api = Api()


def create_app(config_path, name=__name__):
    """
    Method used to create flask application. It will setup logger, CORS, Session, Redis, json serialization,
    blueprints, and default data cleaners
    :param name:
    :param config_path: path to JSON configuration
    :return: configured flask app
    :rtype Flask
    """
    app = Flask(name, static_folder="static", static_url_path="")
    app.config.from_object(config_path)

    # Init SQLAlchemy
    db.init_app(app)

    # Init Marshmallow
    ma.init_app(app)

    # Init Cors
    cors.init_app(app)

    # Init App
    flask_api.init_app(app)

    return app
