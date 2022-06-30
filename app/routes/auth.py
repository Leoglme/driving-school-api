# https://www.askpython.com/python-modules/flask/flask-user-authentication
from datetime import timedelta

import jwt
import redis
from flask import request, redirect, request, render_template, make_response
from werkzeug.security import check_password_hash
from flask import jsonify

from .. import db
from ..models.Token import Token
from ..models.User import User
from .index import router
from flask import Flask, request, render_template
from flask_login import current_user, login_user
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


jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6000, db=0, decode_responses=True
)

ACCESS_EXPIRES = timedelta(hours=1)


@router.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)

    # Returns "Access token revoked" or "Refresh token revoked"
    return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")


