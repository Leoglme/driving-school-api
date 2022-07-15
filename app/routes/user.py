from sqlalchemy import desc

from .index import router
from flask import request
from .. import db
from .. import avatars
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
    role = payload['role_id']
    avatar = avatars.robohash(email, size='80')
    user = User(email=email, first_name=first_name, last_name=last_name, role=role, avatar=avatar)
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
    page = request.args.get('page', 1, type=int)
    take = request.args.get('take', 10, type=int)
    students = User.query.filter_by(role=Role.Student)
    count = students.count()
    if search:
        students = students.filter(User.first_name.contains(search) | User.last_name.contains(search))
        students = students.order_by(desc(User.created_at))
    else:
        students = students.order_by(desc(User.created_at)).paginate(page=page, per_page=take, error_out=False).items

    for student in students:
        student.role = {
            'id': student.role,
            'name': Role(student.role).name
        }

    return jsonify({'students': User.serialize_list(students), 'count': count})


# Get all users != student
@router.route('/employee', methods=['GET'])
def index_employee():
    search = request.args.get("search")
    page = request.args.get('page', 1, type=int)
    take = request.args.get('take', 10, type=int)
    employees = User.query.filter(User.role != Role.Student)

    count = employees.count()
    if search:
        employees = employees.filter(User.first_name.contains(search) | User.last_name.contains(search))
        employees = employees.order_by(desc(User.created_at))
    else:
        employees = employees.order_by(desc(User.created_at)).paginate(page=page, per_page=take, error_out=False).items

    for employee in employees:
        employee.role = {
            'id': employee.role,
            'name': Role(employee.role).name
        }

    return jsonify({'employees': User.serialize_list(employees), 'count': count})


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
        user.role = payload['role_id']
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
