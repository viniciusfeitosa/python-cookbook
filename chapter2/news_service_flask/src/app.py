# src/app.py

from flask import Flask
from flask_migrate import Migrate

from .config import app_config  # import base config
from .models import db  # import ORM database instance

from .views.news import news_api as news_blueprint


# function to load and return an app instance to run.py
def load_app(env_name):
    app = Flask(__name__)  # Instantiate a Flask APP

    app.config.from_object(app_config[env_name])  # Loading configs on Flask

    db.init_app(app)  # integrating ORM instance with Flask APP
    Migrate(app, db)  # Enable migration manager based on models definition

    # Defining routes prefixing all routes with /news
    app.register_blueprint(news_blueprint, url_prefix='/news')

    return app  # return APP instance totally configurated
