# src/app.py

from flask import Flask
from flask_migrate import Migrate

from .config import app_config
from .models import db

from .views.news import news_api as news_blueprint


def load_app(env_name):
    app = Flask(__name__)

    app.config.from_object(app_config[env_name])

    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(news_blueprint, url_prefix='/news')

    @app.route('/', methods=['GET'])
    def index():
        """
        example endpoint
        """
        return 'Congratulations! Your part 2 endpoint is working'

    return app
