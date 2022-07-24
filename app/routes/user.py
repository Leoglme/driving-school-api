from sqlalchemy import desc
from flask_mail import Mail, Message

from .driving_time import update_driving_time
from .index import router
from flask import request, render_template, make_response
from .. import db
from .. import avatars
from ..middleware.auth_middleware import token_required
from ..models.User import User
from flask import jsonify
from ..enums.role import Role

mail = Mail()


# Create user
@router.route('/user', methods=['POST'])
@token_required
def store_user(current_user):
    payload = request.get_json()
    email = payload['email']
    hours_remaining = payload['hours_remaining']
    first_name = payload['first_name']
    password = payload['password']
    last_name = payload['last_name']
    role = payload['role_id']

    # email already use
    user = User.query.filter_by(email=email).first()

    if user:
        return make_response('Un utilisateur existe déjà avec cette adresse mail', 409)

    # Authorize role
    if current_user.role == Role.Student or current_user.role == Role.Instructor or role > current_user.role:
        return 'Not allowed to create user', 401

    avatar = avatars.robohash(email, size='80')
    user = User(email=email, first_name=first_name, last_name=last_name, role=role, avatar=avatar)
    User.set_password(user, password)
    db.session.add(user)
    db.session.commit()

    # Add driving time to user
    update_driving_time(hours_remaining, user.id)

    url = "http://localhost:3000/login"

    msg = Message('Votre compte driving school à été créer', sender='no-reply@driving-school.fr',
                  recipients=[email])
    html = render_template('welcome.html', url=url, password=password)
    msg.html = html
    mail.send(msg)
    return 'User created', 201


# Get all users
@router.route('/users', methods=['GET'])
@token_required
def index_user(current_user):
    search = request.args.get("search")
    limit = request.args.get("limit")
    users = User.query.order_by(desc(User.created_at))

    if current_user.role != Role.Admin:
        users = users.filter(User.role != Role.Admin)

    if search:
        users = users.filter(User.first_name.contains(search) | User.last_name.contains(search))
    if limit:
        users = users.limit(limit)
    return jsonify(User.serialize_list(users))


# Get all users role Student
@router.route('/students', methods=['GET'])
@token_required
def index_students(current_user):
    search = request.args.get("search")
    page = request.args.get('page', 1, type=int)
    take = request.args.get('take', 10, type=int)
    students = User.query.filter_by(role=Role.Student)
    count = students.count()
    if search:
        students = students.filter(User.first_name.contains(search) | User.last_name.contains(search))
        students = students.order_by(desc(User.created_at))
    else:
        students = students.order_by(desc(User.created_at)).paginate(page=page, per_page=take, error_out=False).items

    return jsonify({'students': User.serialize_list(students), 'count': count})


# Get all users != student
@router.route('/employees', methods=['GET'])
@token_required
def index_employee(current_user):
    search = request.args.get('search', "", type=str)
    page = request.args.get('page', 1, type=int)
    take = request.args.get('take', 10, type=int)
    employees = User.query.filter(User.role != Role.Student)
    if current_user.role != Role.Admin:
        employees = employees.filter(User.role != Role.Admin)

    count = employees.count()

    if search:
        employees = employees.filter(User.first_name.contains(search) | User.last_name.contains(search))
        employees = employees.order_by(desc(User.created_at)).all()
    else:
        employees = employees.order_by(desc(User.created_at)).paginate(page=page, per_page=take, error_out=False).items

    return jsonify({'employees': User.serialize_list(employees), 'count': count})


# Get user by id
@router.route('/user/<int:user_id>', methods=['GET'])
@token_required
def show_user(current_user, user_id):
    user = User.query.filter_by(id=user_id).first()
    # Authorize role
    if current_user.role != Role.Admin and user.role == Role.Admin:
        return 'Not allowed to show user', 201
    if user:
        return jsonify(User.serialize(user))
    return f"User with id {user_id} doesn't exist"


# Update user
@router.route('/user/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        payload = request.get_json()

        # email already use
        if user.email != payload['email']:
            email_already_exist = User.query.filter_by(email=payload['email']).first()
            if email_already_exist and current_user.id != user.id:
                return make_response('Un utilisateur existe déjà avec cette adresse mail', 409)

        if current_user.id == user.id and current_user.role < payload['role_id']:
            return 'Not allowed to update user', 401

        # Authorize role
        if (current_user.id != user.id) and (
                current_user.role == Role.Student or
                current_user.role == Role.Instructor or user.role > current_user.role):
            return 'Not allowed to update user', 401

        user.email = payload['email']
        user.first_name = payload['first_name']
        user.last_name = payload['last_name']
        user.role = payload['role_id']

        # Add driving time to user
        update_driving_time(int(payload['hours_remaining']), user.id)

        db.session.commit()
        return 'User Updated'
    return f"User with id {user_id} doesn't exist"


# Delete user
@router.route('/user/<int:user_id>', methods=['DELETE'])
@token_required
def destroy_user(current_user, user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        # Authorize role
        if current_user.id == user.id or current_user.role == Role.Student or current_user.role == Role.Instructor or user.role > current_user.role:
            return 'Non autorisé à supprimer l\'utilisateur', 401

        db.session.delete(user)
        db.session.commit()
        return 'User deleted'
    return f"L'utilisateur avec l'identifiant {user_id} n'existe pas"
