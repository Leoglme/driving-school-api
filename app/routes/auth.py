# https://www.askpython.com/python-modules/flask/flask-user-authentication
from datetime import timedelta

import jwt
import redis
from flask import request, redirect, request, render_template, make_response, current_app
from werkzeug.security import check_password_hash
from flask import jsonify

from .. import db
from ..models.Token import Token
from ..models.User import User
from .index import router
from flask import Flask, request, render_template
from flask_login import current_user, login_user, logout_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt


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
        token = jwt.encode({'id': user.id}, "toto", 'HS256')
        print(token)
        token = Token(token=token, user_id=user.id)
        db.session.add(token)
        db.session.commit()
        return make_response(jsonify({'token': token}), 201)

    return make_response('Could not verify password!', 403, {'WWW-Authenticate': 'Basic-realm= "Wrong Password!"'})


# @router.route("/logout/<int:user_id>", methods=["DELETE"])
# @jwt_required()
# def logout(user_id):
#     user = request.get_json()
#     token = request.get_json()
#     if token.get('token') and user.get('user_id'):
#         db.session.delete(token)
#     return make_response(user_id, 204)

ACCESS_EXPIRES = timedelta(hours=1)

jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6000, db=0, decode_responses=True
)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


@router.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
    return jsonify(msg="Access token revoked")
