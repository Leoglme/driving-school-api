from sqlalchemy import desc, and_
from flask_mail import Mail, Message

from .driving_time import update_driving_time
from flask import request, render_template, make_response, Blueprint
from .. import avatars
from ..middleware.auth_middleware import token_required
from ..models.User import User
from flask import jsonify
from ..enums.role import Role
from flask import current_app
from .. import mail
import os

router = Blueprint('user', __name__)


# Create user
@router.route('/user', methods=['POST'])
@token_required
def store_user(current_user):
    from .. import db
    payload = request.get_json()
    email = payload['email']
    hours_remaining = payload['hours_remaining'] if 'hours_remaining' in payload and payload['hours_remaining'] is not None else 0
    first_name = payload['first_name']
    password = payload['password']
    last_name = payload['last_name']
    role = payload['role_id']

    # Vérifier si l'email existe déjà
    user = User.query.filter_by(email=email).first()
    if user:
        return make_response('Un utilisateur existe déjà avec cette adresse mail', 409)

    # Vérifier les autorisations de rôle
    if current_user.role == Role.Student.value or current_user.role == Role.Instructor.value or role > current_user.role:
        return 'Not allowed to create user', 401

    # Créer l'utilisateur
    avatar = avatars.robohash(email, size='80')
    user = User(email=email, first_name=first_name, last_name=last_name, role=role, avatar=avatar)
    User.set_password(user, password)
    db.session.add(user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    # Ajouter le temps de conduite
    update_driving_time(hours_remaining, user.id)

    # Envoyer l'e-mail de bienvenue
    url = os.getenv("FRONTEND_URL", "http://localhost:3000") + f"/login"
    msg = Message('Votre compte driving school a été créé', sender='no-reply@driving-school.fr', recipients=[email])
    html = render_template('welcome.html', url=url, password=password)
    msg.html = html
    try:
        mail.send(msg)
        current_app.logger.info(f"E-mail envoyé à {email}")
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de l'e-mail à {email} : {str(e)}")
        # Ne pas échouer la création de l'utilisateur en cas d'erreur d'e-mail
        return make_response('Utilisateur créé, mais erreur lors de l\'envoi de l\'e-mail', 201)

    return 'User created', 201


# Get all users
@router.route('/users', methods=['GET'])
@token_required
def index_user(current_user):
    search = request.args.get("search")
    limit = request.args.get("limit")
    users = User.query.filter(User.active.is_(True)).order_by(desc(User.created_at))

    if current_user.role != Role.Admin.value:
        users = users.filter(User.role != Role.Admin.value)

    if search:
        users = users.filter(User.first_name.contains(search) | User.last_name.contains(search))
    if limit:
        users = users.limit(limit)
    users = users.all()
    return jsonify(User.serialize_list(users))


# Get all users role Student
@router.route('/students', methods=['GET'])
@token_required
def index_students(current_user):
    try:
        search = request.args.get("search")
        page = request.args.get('page', 1, type=int)
        take = request.args.get('take', 10, type=int)
        current_app.logger.info(f"STUDENTS - Paramètres : search={search}, page={page}, take={take}")

        students = User.query.filter(and_(User.role == Role.Student.value, User.active.is_(True)))

        count = students.count()

        if search:
            students = students.filter(User.first_name.contains(search) | User.last_name.contains(search))
            students = students.order_by(desc(User.created_at)).all()
        else:
            students = students.order_by(desc(User.created_at)).paginate(page=page, per_page=take,
                                                                         error_out=False).items

        return jsonify({'students': User.serialize_list(students), 'count': count})
    except Exception as e:
        current_app.logger.error(f"STUDENTS - Erreur : {str(e)}", exc_info=True)
        raise


# Get all users != student
@router.route('/employees', methods=['GET'])
@token_required
def index_employee(current_user):
    try:
        current_app.logger.info("EMPLOYEES - Début de la route")
        search = request.args.get('search', "", type=str)
        page = request.args.get('page', 1, type=int)
        take = request.args.get('take', 10, type=int)
        current_app.logger.info(f"EMPLOYEES - Paramètres : search={search}, page={page}, take={take}")

        employees = User.query.filter(and_(User.role != Role.Student.value, User.active.is_(True)))
        current_app.logger.info("EMPLOYEES - Requête SQL créée")

        if current_user.role != Role.Admin.value:
            employees = employees.filter(User.role != Role.Admin.value)
            current_app.logger.info("EMPLOYEES - Filtre non-admin appliqué")

        count = employees.count()
        current_app.logger.info(f"EMPLOYEES - Nombre d'employés trouvés : {count}")

        if search:
            employees = employees.filter(User.first_name.contains(search) | User.last_name.contains(search))
            employees = employees.order_by(desc(User.created_at)).all()
            current_app.logger.info("EMPLOYEES - Recherche appliquée")
        else:
            employees = employees.order_by(desc(User.created_at)).paginate(page=page, per_page=take,
                                                                           error_out=False).items
            current_app.logger.info("EMPLOYEES - Pagination appliquée")

        current_app.logger.info(f"EMPLOYEES - Rôles des employés : {[u.role for u in employees]}")
        return jsonify({'employees': User.serialize_list(employees), 'count': count})
    except Exception as e:
        current_app.logger.error(f"EMPLOYEES - Erreur : {str(e)}", exc_info=True)
        raise


# Get user by id
@router.route('/user/<int:user_id>', methods=['GET'])
@token_required
def show_user(current_user, user_id):
    user = User.query.filter_by(id=user_id).first()
    # Authorize role
    if current_user.role != Role.Admin.value and user.role == Role.Admin.value:
        return 'Not allowed to show user', 201
    if user:
        return jsonify(User.serialize(user))
    return f"User with id {user_id} doesn't exist"


# Update user
@router.route('/user/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    from .. import db
    user = User.query.filter_by(id=user_id).first()
    if user:
        user_admin_email = 'admin@driving-school.dibodev.fr'
        # if email == user_admin_email return 401
        if user.email == user_admin_email:
            return make_response('Vous ne pouvez pas modifier cet utilisateur', 401,
                                 {'WWW-Authenticate': 'Basic-realm= "Unauthorized!"'})
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
                current_user.role in [Role.Student.value, Role.Instructor.value]
                or user.role > current_user.role
        ):
            return 'Not allowed to update user', 401

        user.email = payload['email']
        user.first_name = payload['first_name']
        user.last_name = payload['last_name']
        user.role = payload['role_id']

        # if payload hours_remaining update driving time
        if 'hours_remaining' in payload and payload['hours_remaining'] is not None:
            # Add driving time to user
            update_driving_time(int(payload['hours_remaining']), user.id)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return 'User Updated'
    return f"User with id {user_id} doesn't exist"


# Delete user
@router.route('/user/<int:user_id>', methods=['DELETE'])
@token_required
def destroy_user(current_user, user_id):
    from .. import db
    user = User.query.filter_by(id=user_id).first()
    if user:
        user_admin_email = 'admin@driving-school.dibodev.fr'
        # if email == user_admin_email return 401
        if user.email == user_admin_email:
            return make_response('Vous ne pouvez pas supprimer cet utilisateur', 401,
                                 {'WWW-Authenticate': 'Basic-realm= "Unauthorized!"'})

        # Authorize role
        if (
                current_user.id == user.id
                or current_user.role in [Role.Student.value, Role.Instructor.value]
                or user.role > current_user.role
        ):
            return 'Non autorisé à supprimer l\'utilisateur', 401

        user.active = False
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return 'User deleted'
    return f"L'utilisateur avec l'identifiant {user_id} n'existe pas"
