from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])

    bootstrap.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from .main_blueprint import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
