# https://www.askpython.com/python-modules/flask/flask-user-authentication
import jwt
from flask import make_response, session
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash
from flask import jsonify
from datetime import datetime, timedelta
from main import app
from .. import db
from ..models.Token import Token
from ..models.User import User
from .index import router
from flask import request


@router.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('email') or not auth.get('password'):
        return make_response('oupla!', 401, {'WWW-Authenticate': 'Basic-realm= "Login required!"'})

    user = User.query.filter_by(email=auth['email']).first()
    if not user:
        return make_response('Could not verify user, Please signup!', 401,
                             {'WWW-Authenticate': 'Basic-realm= "No user found!"'})

    if check_password_hash(user.password, auth.get('password')):
        # Delete oldest token
        old_token = Token.query.filter_by(user_id=user.id).first()
        db.session.delete(old_token)
        db.session.commit()

        # Create and add New Token
        token = jwt.encode({'id': user.id}, app.config['SECRET_KEY'], 'HS256')
        token = Token(token=token, user_id=user.id)
        db.session.add(token)
        db.session.commit()

        return make_response(jsonify({'token': token.serialize()}), 201)

    return make_response('Could not verify password!', 403, {'WWW-Authenticate': 'Basic-realm= "Wrong Password!"'})


# @router.route("/logout/<int:user_id>", methods=["DELETE"])
# @jwt_required()
# def logout(user_id):
#     user = request.get_json()
#     token = request.get_json()
#     if token.get('token') and user.get('user_id'):
#         db.session.delete(token)
#     return make_response(user_id, 204)

# ACCESS_EXPIRES = timedelta(hours=1)
#
# jwt_redis_blocklist = redis.StrictRedis(
#     host="localhost", port=6000, db=0, decode_responses=True
# )
#
#
# @jwt.token_in_blocklist_loader
# def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
#     jti = jwt_payload["jti"]
#     token_in_redis = jwt_redis_blocklist.get(jti)
#     return token_in_redis is not None


# @router.route("/logout", methods=["DELETE"])
# @jwt_required()
# def logout():
#     jti = get_jwt()["jti"]
#     # jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
#     return jsonify(msg="Access token revoked")

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

    token = jwt.encode({
        'email': email,
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, app.config['SECRET_KEY'])

    url = "http://localhost:3000/reset-password/" + token

    msg = Message('Hello', sender='no-reply@driving-school.fr', recipients=[email])
    msg.body = url
    mail.send(msg)

    return make_response('Email sent at ' + email, 200)


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
