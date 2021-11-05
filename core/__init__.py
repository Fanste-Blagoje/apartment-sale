__author__ = "Stefan"

from flask import Flask,  request, current_app
from flask_restful import Api
from flask_cors import CORS
from flask_marshmallow import Marshmallow
import logging
from logging.handlers import RotatingFileHandler
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

    # Configure logs
    # _configure_log(app)

    # @app.before_request
    # # Ask Uros for this
    # def before_request():
    #     if request.method == 'OPTIONS' or '/static/' in request.path or "/apple-app-site-association" in request.path:
    #         return
    #
    #     if request.method != 'GET':
    #         current_app.logger.info("[REQUEST - {}] - URL: {}, arguments: {}, json: {}".format(
    #             request.method, request.base_url, request.values, request.json))
    #
    # @app.after_request
    # def after_request(response):
    #     db.session.commit()
    #     if request.method != 'GET':
    #         current_app.logger.info("[RESPONSE] - URL: {}, response: {}".format(request.base_url, response.get_data()))
    #     return response

    return app


# Ask Uros for this
# def _configure_log(app):
#     rotation_handler = RotatingFileHandler(
#         app.config.get("LOG_PATH"), backupCount=app.config.get("LOG_COUNT"),
#         maxBytes=app.config.get("LOG_MAX_SIZE"), encoding=app.config.get("LOG_ENCODING"))
#     rotation_handler.setLevel(app.config.get("LOG_LEVEL"))
#     formatter = logging.Formatter(
#         "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
#     rotation_handler.setFormatter(formatter)
#     app.logger.addHandler(rotation_handler)
#     app.logger.setLevel(app.config.get("LOG_LEVEL"))