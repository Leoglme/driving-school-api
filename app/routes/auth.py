# https://www.askpython.com/python-modules/flask/flask-user-authentication
import jwt
from flask import make_response, session, render_template
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash
from flask import jsonify
from datetime import datetime, timedelta
from main import app
from .. import db
from ..middleware.auth_middleware import token_required
from ..models.Token import Token
from ..models.User import User
from .index import router
from flask import request


@router.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('email') or not auth.get('password'):
        return make_response('Champ du formulaire incorrect', 401,
                             {'WWW-Authenticate': 'Basic-realm= "Login required!"'})

    user = User.query.filter_by(email=auth['email']).first()

    if not user:
        return make_response('Aucun utilisateur trouvé avec cette adresse email', 401,
                             {'WWW-Authenticate': 'Basic-realm= "No user found!"'})

    if check_password_hash(user.password, auth.get('password')):
        # Delete oldest token
        old_token = Token.query.filter_by(user_id=user.id).first()
        if old_token:
            db.session.delete(old_token)
            db.session.commit()

        # Create and add New Token
        token = jwt.encode({'id': user.id}, app.config['SECRET_KEY'], 'HS256')
        token = Token(token=token, user_id=user.id)
        db.session.add(token)
        db.session.commit()

        return make_response(jsonify({
            'passwordNeedSet': user.passwordNeedSet,
            'token': token.serialize(),
            'user': User.serialize(user)
        }), 201)

    return make_response('Mot de passe incorrect', 403, {'WWW-Authenticate': 'Basic-realm= "Wrong Password!"'})


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

    user = User.query.filter_by(email=email).first()

    if not user:
        return make_response('Aucun utilisateur trouvé avec cette adresse email', 401,
                             {'WWW-Authenticate': 'Basic-realm= "No user found!"'})

    token = jwt.encode({
        'email': email,
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, app.config['SECRET_KEY'])

    url = "http://localhost:3000/reset-password?token=" + token

    msg = Message('Demande de changement de mot de passe Driving school', sender='no-reply@driving-school.fr',
                  recipients=[email])
    html = render_template('reset-password.html', url=url)
    msg.html = html
    mail.send(msg)

    return make_response('Email envoyé à ' + email, 200)


@router.route('/create-password', methods=["PUT"])
@token_required
def create_password(current_user):
    token = request.headers.get('Authorization')
    payload = request.get_json()
    password = payload['password']

    decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    user_id = decoded_token['id']
    user = User.query.filter_by(id=user_id).first()
    user.passwordNeedSet = False
    user.set_password(password)
    db.session.commit()

    return make_response({'user': user.serialize()}, 201)


@router.route('/reset-password/<string:token>', methods=["POST"])
def reset_password(token):
    payload = request.get_json()
    password = payload['password']

    decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    email = decoded_token['email']
    user = User.query.filter_by(email=email).first()

    user.set_password(password)
    db.session.commit()

    return make_response('', 204)
