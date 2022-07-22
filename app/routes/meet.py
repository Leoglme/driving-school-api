from sqlalchemy import desc

from .driving_time import add_driving_time
from .index import router
from flask import request
from .. import db
from ..enums.role import Role
from ..middleware.auth_middleware import token_required
from ..models.Meet import Meet
from ..models.DrivingTime import DrivingTime
from flask import jsonify
from datetime import datetime

# Create meet
from ..models.User import User


@router.route('/meet', methods=['POST'])
@token_required
def store_meet(current_user):
    # Authorize role
    if current_user.role == Role.Student:
        return 'Not allowed to create meet', 401
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

    if user.role == Role.Student:
        driving_time_remaining = DrivingTime.query.filter_by(user_id=user_id).first()
        if driving_time_remaining and driving_time_remaining.hours_total - (driving_time_remaining.hours_done + between_hours) < 0:
            return "L'utilisateur " + user.first_name + " " + user.last_name + " n'a plus d'heure disponible", 401
        add_driving_time(between_hours, user.id)

    if chef.role == Role.Student:
        driving_time_remaining = DrivingTime.query.filter_by(user_id=chef_id).first()
        if driving_time_remaining and driving_time_remaining.hours_total - (driving_time_remaining.hours_done + between_hours) < 0:
            return "L'utilisateur " + chef.first_name + " " + chef.last_name + " n'a plus d'heure disponible", 401
        add_driving_time(between_hours, chef.id)

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
        return 'Not allowed to create meet', 401
    meet = Meet.query.filter_by(id=meet_id).first()
    if meet:
        payload = request.get_json()
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
        return 'Not allowed to create meet', 401
    meet = Meet.query.filter_by(id=meet_id).first()
    if meet:
        db.session.delete(meet)
        db.session.commit()
        return 'Meet deleted'
    return f"Meet with id {meet_id} doesn't exist"
