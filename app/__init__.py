from flask import Flask

from .routes.index import router
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_cors import CORS
from flask_avatars import Avatars

avatars = Avatars()
# Init the database
db = SQLAlchemy()
DB_NAME = "driving-school.db"


def create_app():
    app = Flask(__name__)
    CORS(app)

    # App configs
    app.config['SECRET_KEY'] = 'lorem ipsum'
    # Database path
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    # Disable create db deprecated warning
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 1025
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = ""
    app.config['MAIL_PASSWORD'] = ""

    db.init_app(app)

    # Import models
    from .models import User, Role, Meet, Token, DrivingTime

    # Import routes
    from .routes import user, auth, user, meet, role, driving_time

    app.register_blueprint(router)

    create_database(app)

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

