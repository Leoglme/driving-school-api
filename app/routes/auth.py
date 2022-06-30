# https://www.askpython.com/python-modules/flask/flask-user-authentication
import jwt
from flask import request, redirect, request, render_template, make_response
from werkzeug.security import check_password_hash
from flask import jsonify
from ..models.User import User
from .index import router
from flask import Flask, request, render_template
from flask_login import current_user, login_user
from flask_jwt_extended import create_access_token
# from flask_login import current_user, login_user


#
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
        return make_response(jsonify({'token': token}), 201)

    return make_response('Could not verify password!', 403, {'WWW-Authenticate': 'Basic-realm= "Wrong Password!"'})
    # email = request.json.get('email', None)
    # password = request.json.get('password', None)
    #
    # try:
    #     user = User.query.find_one({"Email": email})
    #
    #     if user is None:
    #         raise Exception("User not found")
    #
    #     valid = check_password_hash(user['password'], password)
    #     if not valid:
    #         raise Exception('Password not correct')
    #
    #     token = create_access_token(identity=user['id'], expires_delta=None)
    #
    #     result = {'token': token}
    #     return jsonify(result), 200
    # except Exception as e:
    #     return jsonify({'Error': repr(e)})
#
#
# @router.route('/logout', methods=['POST'])
# @jwt_required()
# def logout():
#     jti = get_jwt()['jti']
#     blacklist.add(jti)
#     return jsonify({"message": "Successfully logged out"}), 200

# @router.route('/login', methods=['POST', 'GET'])
# def login():
#     if current_user.is_authenticated:
#         return redirect('/blogs')
#
#     if request.method == 'POST':
#         email = request.form['email']
#         user = User.query.filter_by(email=email).first()
#         if user is not None and user.check_password(request.form['password']):
#             login_user(user)
#             return redirect('/blogs')
#
#     return render_template('')
