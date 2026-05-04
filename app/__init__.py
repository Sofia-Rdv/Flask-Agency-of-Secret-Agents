from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from logging_module.my_logger_config import setup_logging

# Создаем объекты базы данных и приложения
db = SQLAlchemy()
setup_logging()


def create_app():
    app = Flask(__name__)
    app.secret_key = 'batman_secret_access_key'

    # Настройка базы данных SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../gotham_intel.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from app import routes
        from app.models import Agent
        # Создаем таблицы если их нет
        db.create_all()
    return app