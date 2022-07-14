from .index import router
from flask import request
from .. import db
from ..models.User import User
from flask import jsonify
from ..enums.role import Role


# Create user
@router.route('/user', methods=['POST'])
def store_user():
    payload = request.get_json()
    email = payload['email']
    first_name = payload['first_name']
    last_name = payload['last_name']
    role = payload['role']
    user = User(email=email, first_name=first_name, last_name=last_name, role=role)
    User.set_password(user, payload['password'])
    db.session.add(user)
    db.session.commit()
    return 'User created', 201


# Get all users
@router.route('/users', methods=['GET'])
def index_user():
    users = User.query.all()
    return jsonify(User.serialize_list(users))


# Get all users role Student
@router.route('/students', methods=['GET'])
def index_students():
    search = request.args.get("search")
    users = User.query.filter_by(role=Role.Student)
    if search:
        users = users.filter(User.first_name.contains(search))
    # users = users.contains(first_name=search)
    return jsonify(User.serialize_list(users))


# Get all users != student
@router.route('/employee', methods=['GET'])
def index_employee():
    users = User.query.filter(User.role != Role.Student).all()
    return jsonify(User.serialize_list(users))


# Get user by id
@router.route('/user/<int:user_id>', methods=['GET'])
def show_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.role = {
        'id': user.role,
        'name': Role(user.role).name
    }
    if user:
        return jsonify(User.serialize(user))
    return f"User with id {user_id} doesn't exist"


# Update user
@router.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        payload = request.get_json()
        user.email = payload['email']
        user.first_name = payload['first_name']
        user.last_name = payload['last_name']
        user.role_id = payload['role_id']
        db.session.commit()
        return 'User Updated'
    return f"User with id {user_id} doesn't exist"


# Delete user
@router.route('/user/<int:user_id>', methods=['DELETE'])
def destroy_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return 'User deleted'
    return f"User with id {user_id} doesn't exist"
