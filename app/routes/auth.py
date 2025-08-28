# https://www.askpython.com/python-modules/flask/flask-user-authentication
import jwt
from flask import make_response, session, render_template, Blueprint, current_app
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash
from flask import jsonify
from flask import current_app as app
from datetime import datetime, timedelta
from ..middleware.auth_middleware import token_required
from ..models.Token import Token
from ..models.User import User
from .. import db
from flask import request
import os

router = Blueprint('auth', __name__)


@router.route('/login', methods=['POST'])
def login():
    try:
        current_app.logger.info("Début de la route /login")
        auth = request.get_json()
        current_app.logger.info(f"Données reçues : {auth}")

        if not auth or not auth.get('email') or not auth.get('password'):
            current_app.logger.error("Champ du formulaire incorrect : email ou mot de passe manquant")
            return make_response('Champ du formulaire incorrect', 401,
                                 {'WWW-Authenticate': 'Basic-realm= "Login required!"'})

        current_app.logger.info(f"Recherche de l'utilisateur avec l'email : {auth['email']}")
        user = User.query.filter_by(email=auth['email']).first()

        if not user:
            current_app.logger.error(f"Aucun utilisateur trouvé avec l'email : {auth['email']}")
            return make_response('Aucun utilisateur trouvé avec cette adresse email', 401,
                                 {'WWW-Authenticate': 'Basic-realm= "No user found!"'})

        current_app.logger.info(f"Vérification du mot de passe pour l'utilisateur : {user.email}")
        if check_password_hash(user.password, auth.get('password')):
            current_app.logger.info(f"Mot de passe correct pour l'utilisateur : {user.email}")

            # Delete oldest token
            old_token = Token.query.filter_by(user_id=user.id).first()
            if old_token:
                current_app.logger.info(f"Suppression de l'ancien token pour l'utilisateur : {user.id}")
                db.session.delete(old_token)
                db.session.commit()

            # Create and add New Token
            current_app.logger.info(f"Génération d'un nouveau token pour l'utilisateur : {user.id}")
            secret_key = current_app.config.get('SECRET_KEY')
            if not secret_key:
                current_app.logger.error("SECRET_KEY non défini dans la configuration")
                return make_response(jsonify({'error': 'Configuration serveur incorrecte : clé secrète manquante'}), 500)
            current_app.logger.info(f"Clé secrète utilisée : {secret_key}")
            token = jwt.encode({'id': user.id, 'exp': datetime.utcnow() + timedelta(hours=24)},
                             secret_key, algorithm='HS256')
            current_app.logger.info(f"Token généré : {token}")

            token_obj = Token(token=token, user_id=user.id)
            db.session.add(token_obj)
            db.session.commit()
            current_app.logger.info(f"Nouveau token ajouté à la base pour l'utilisateur : {user.id}")

            return make_response(jsonify({
                'passwordNeedSet': user.passwordNeedSet,
                'token': token_obj.serialize(),
                'user': User.serialize(user)
            }), 201)

        current_app.logger.error(f"Mot de passe incorrect pour l'utilisateur : {user.email}")
        return make_response('Mot de passe incorrect', 403, {'WWW-Authenticate': 'Basic-realm= "Wrong Password!"'})
    except Exception as e:
        current_app.logger.error(f"Erreur dans la route /login : {str(e)}", exc_info=True)
        return make_response(jsonify({'error': 'Erreur interne du serveur'}), 500)


@router.route('/logout', methods=["GET"])
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('email', None)
    session.pop('id', None)
    return make_response('yes', 200)


@router.route('/forgot-password', methods=["POST"])
def forgot_password():
    mail = Mail(app)

    payload = request.get_json()
    email = payload['email']
    user_admin_email = 'admin@driving-school.dibodev.fr'
    # if email == user_admin_email return 401
    if email == user_admin_email:
        return make_response('Vous ne pouvez pas modifier le mot de passe de cet utilisateur', 401,
                             {'WWW-Authenticate': 'Basic-realm= "Unauthorized!"'})

    user = User.query.filter_by(email=email).first()

    if not user:
        return make_response('Aucun utilisateur trouvé avec cette adresse email', 401,
                             {'WWW-Authenticate': 'Basic-realm= "No user found!"'})

    token = jwt.encode({
        'email': email,
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    url = os.getenv("FRONTEND_URL", "http://localhost:3000") + f"/reset-password?token={token}"

    msg = Message('Demande de changement de mot de passe Driving school', sender='no-reply@driving-school.fr',
                  recipients=[email])
    html = render_template('reset-password.html', url=url)
    msg.html = html
    mail.send(msg)

    return make_response('Email envoyé à ' + email, 200)


@router.route('/create-password', methods=["PUT"])
@token_required
def create_password(current_user):
    try:
        user_admin_email = 'admin@driving-school.dibodev.fr'
        # if email == user_admin_email return 401
        if current_user.email == user_admin_email:
            return make_response('Vous ne pouvez pas modifier le mot de passe de cet utilisateur', 401,
                                 {'WWW-Authenticate': 'Basic-realm= "Unauthorized!"'})

        current_app.logger.info(f"Début de la route /create-password pour l'utilisateur : {current_user.email}")
        payload = request.get_json()
        current_app.logger.info(f"Données reçues : {payload}")
        password = payload.get('password')

        if not password:
            current_app.logger.error("Mot de passe manquant dans la requête")
            return make_response(jsonify({'error': 'Mot de passe requis'}), 400)

        from .. import db
        current_user.passwordNeedSet = False
        current_user.set_password(password)
        db.session.commit()
        current_app.logger.info(f"Mot de passe mis à jour pour l'utilisateur : {current_user.email}")

        return make_response(jsonify({'user': current_user.serialize()}), 201)
    except Exception as e:
        current_app.logger.error(f"Erreur dans la route /create-password : {str(e)}", exc_info=True)
        return make_response(jsonify({'error': 'Erreur interne du serveur'}), 500)


@router.route('/reset-password/<string:token>', methods=["POST"])
def reset_password(token):
    from .. import db
    payload = request.get_json()
    password = payload['password']

    decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    email = decoded_token['email']
    user = User.query.filter_by(email=email).first()

    user_admin_email = 'admin@driving-school.dibodev.fr'
    # if email == user_admin_email return 401
    if email == user_admin_email:
        return make_response('Vous ne pouvez pas modifier le mot de passe de cet utilisateur', 401,
                             {'WWW-Authenticate': 'Basic-realm= "Unauthorized!"'})

    user.set_password(password)
    db.session.commit()

    return make_response('', 204)
