from api import user, customer, apartment, reports
import flask
from core import db, create_app as create_flask_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server
import models

public_blueprint = flask.Blueprint('verification', __name__, template_folder="templates", static_folder="static")


def create_app():
    """
    Create Flask Application
    """

    app = create_flask_app(config_path="config.APPConfig", name=__name__)

    # Register public routes
    app.register_blueprint(public_blueprint, url_prefix="/public")

    return app


app = create_app()

manager = Manager(app)
migrate = Migrate()
server = Server(host="0.0.0.0", port=5000)
manager.add_command('runserver', server)
migrate.init_app(app, db)
manager.add_command('db', MigrateCommand)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    manager.run()

