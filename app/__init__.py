from flask import Flask, jsonify

from .routes.index import router
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_cors import CORS
from flask_avatars import Avatars
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from flask_mail import Mail

avatars = Avatars()
# Init the database
db = SQLAlchemy()
mail = Mail()


def create_app():
    app = Flask(__name__)
    # Configurer le niveau de logging
    app.logger.setLevel(logging.INFO)

    # Créer un handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Définir un format pour les logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Ajouter le handler au logger de l'application
    app.logger.addHandler(console_handler)

    # Gestionnaire d'erreurs global
    @app.errorhandler(Exception)
    def handle_error(error):
        app.logger.error(f"Erreur non gérée : {str(error)}", exc_info=True)
        return jsonify({"error": "Erreur interne du serveur"}), 500

    CORS(app)

    # Charger .env
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    # Configurer SECRET_KEY
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    if not app.config['SECRET_KEY']:
        app.logger.warning("SECRET_KEY non défini dans .env, utilisation de la valeur par défaut")
        app.config['SECRET_KEY'] = "default-secret-key-for-testing"  # Valeur par défaut pour tests
    app.logger.info(f"SECRET_KEY configurée : {app.config['SECRET_KEY']}")

    # Database config
    DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")
    if DB_ENGINE == "sqlite":
        DB_NAME = os.getenv("DB_NAME", "driving-school.db")
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    else:
        DB_USER = os.getenv("DB_USER", "root")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "3306")
        DB_NAME = os.getenv("DB_NAME", "driving_school")
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Mail config
    app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER", "localhost")
    app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT", 1025))
    app.config['MAIL_USE_SSL'] = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", "")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", "")

    db.init_app(app)
    mail.init_app(app)

    # Import models
    from .models import User, Role, Meet, Token, DrivingTime

    # Import routes
    from .routes import user, auth, meet, role, driving_time

    # Enregistrement des blueprints après que toutes les routes sont définies
    app.register_blueprint(auth.router)
    app.register_blueprint(user.router)
    app.register_blueprint(meet.router)
    app.register_blueprint(role.router)
    app.register_blueprint(driving_time.router)

    return app

