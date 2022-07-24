from sqlalchemy import desc

from .driving_time import set_driving_time
from .index import router
from flask import request
from .. import db
from ..enums.role import Role
from ..middleware.auth_middleware import token_required
from ..models.Meet import Meet
from ..models.DrivingTime import DrivingTime
from ..models.User import User
from flask import jsonify
from datetime import datetime


def update_meet_driving_time(user, chef, between_hours):
    if user.role == Role.Student:
        driving_time_remaining = DrivingTime.query.filter_by(user_id=user.id).first()

        if driving_time_remaining and driving_time_remaining.hours_total - (
                driving_time_remaining.hours_done + between_hours) < 0:
            raise Exception("L'utilisateur " + user.first_name + " " + user.last_name + " n'a plus d'heure disponible")
        set_driving_time(between_hours, user.id)

    if chef.role == Role.Student:
        driving_time_remaining = DrivingTime.query.filter_by(user_id=chef.id).first()
        if driving_time_remaining and driving_time_remaining.hours_total - (
                driving_time_remaining.hours_done + between_hours) < 0:
            raise Exception("L'utilisateur " + chef.first_name + " " + chef.last_name + " n'a plus d'heure disponible")
        set_driving_time(between_hours, chef.id)


# Create meet
@router.route('/meet', methods=['POST'])
@token_required
def store_meet(current_user):
    # Authorize role
    if current_user.role == Role.Student:
        return 'Non autorisé à créer un rendez-vous', 401
    payload = request.get_json()
    title = payload['title']
    start = datetime.fromisoformat(payload['start'])
    end = datetime.fromisoformat(payload['end'])
    all_day = payload['allDay']
    chef_id = payload['chef']
    user_id = payload['user']

    # Add Driving time
    user = User.query.filter_by(id=user_id).first()
    chef = User.query.filter_by(id=chef_id).first()

    # convert string to date object
    d1 = datetime.strptime(payload['start'], "%Y-%m-%d %H:%M:%S")
    d2 = datetime.strptime(payload['end'], "%Y-%m-%d %H:%M:%S")

    # difference between dates in timedelta
    between_hours = round(abs((d2 - d1).seconds) / 3600)

    try:
        update_meet_driving_time(user, chef, between_hours)
    except Exception as e:
        return str(e), 500

    meet = Meet(title=title, start=start, end=end, all_day=all_day, chef=chef_id, user=user_id)
    db.session.add(meet)
    db.session.commit()
    return 'Meet created', 201


# Get all meets
@router.route('/meets', methods=['GET'])
@token_required
def index_meet(current_user):
    user_id = request.args.get('user_id', type=int)
    meets = Meet.query.order_by(desc(Meet.created_at))
    authorize_show_all = current_user.role >= Role.Secretary.value

    if not authorize_show_all:
        meets = meets.filter((Meet.user == current_user.id) | (Meet.chef == current_user.id))
        return jsonify(Meet.serialize_list(meets))

    if user_id:
        meets = meets.filter(Meet.user == user_id or Meet.chef == user_id)
    return jsonify(Meet.serialize_list(meets))


# Get meet by userId
@router.route('/meet/<int:user_id>', methods=['GET'])
@token_required
def meets_by_user_id(current_user, user_id):
    meets = Meet.query.order_by(desc(Meet.created_at))
    meets = meets.filter(Meet.chef.__eq__(user_id) | Meet.user.__eq__(user_id))
    return jsonify(Meet.serialize_list(meets))


# Update meet
@router.route('/meet/<int:meet_id>', methods=['PUT'])
@token_required
def update_meet(current_user, meet_id):
    # Authorize role
    if current_user.role == Role.Student:
        return 'Non autorisé à créer un rendez-vous', 401
    meet = Meet.query.filter_by(id=meet_id).first()
    if meet:
        payload = request.get_json()

        # Add Driving time
        user = User.query.filter_by(id=payload['chef']).first()
        chef = User.query.filter_by(id=payload['user']).first()

        # convert string to date object
        datetime_format = "%Y-%m-%d %H:%M:%S"
        start = datetime.strptime(datetime.strftime(meet.start, datetime_format), datetime_format)
        end = datetime.strptime(datetime.strftime(meet.end, datetime_format), datetime_format)

        new_start = datetime.strptime(payload['start'], datetime_format)
        new_end = datetime.strptime(payload['end'], datetime_format)
        # difference between dates in timedelta
        between_hours = round(
            round(abs((new_end - new_start).seconds) / 3600) - round(abs((end - start).seconds) / 3600))

        try:
            update_meet_driving_time(user, chef, between_hours)
        except Exception as e:
            return str(e), 500

        meet.title = payload['title']
        meet.start = datetime.fromisoformat(payload['start'])
        meet.end = datetime.fromisoformat(payload['end'])
        meet.all_day = payload['allDay']
        meet.chef = payload['chef']
        meet.user = payload['user']

        db.session.commit()
        return 'Meet Updated'
    return f"Meet with id {meet_id} doesn't exist"


# Delete meet
@router.route('/meet/<int:meet_id>', methods=['DELETE'])
@token_required
def destroy_meet(current_user, meet_id):
    # Authorize role
    if current_user.role == Role.Student:
        return 'Non autorisé à créer un rendez-vous', 401
    meet = Meet.query.filter_by(id=meet_id).first()
    if meet:
        # Add Driving time
        user = User.query.filter_by(id=meet.chef).first()
        chef = User.query.filter_by(id=meet.user).first()

        # convert string to date object
        datetime_format = "%Y-%m-%d %H:%M:%S"
        start = datetime.strptime(datetime.strftime(meet.start, datetime_format), datetime_format)
        end = datetime.strptime(datetime.strftime(meet.end, datetime_format), datetime_format)

        # difference between dates in timedelta
        between_hours = round(-abs((end - start).seconds) / 3600)

        try:
            update_meet_driving_time(user, chef, between_hours)
        except Exception as e:
            return str(e), 500

        db.session.delete(meet)
        db.session.commit()
        return 'Meet deleted'
    return f"Meet with id {meet_id} doesn't exist"
