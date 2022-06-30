from flask import Flask
from .routes.index import router
from flask_sqlalchemy import SQLAlchemy
from os import path

# Init the database
db = SQLAlchemy()
DB_NAME = "driving-school.db"


def create_app():
    app = Flask(__name__)

    # App configs
    app.config['SECRET_KEY'] = 'lorem ipsum'
    # Database path
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    # Disable create db deprecated warning
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Import models
    from .models import User, Role, Meet, Token, Time

    # Import routes
    from .routes import user, auth, user, meet

    app.register_blueprint(router)

    create_database(app)

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

