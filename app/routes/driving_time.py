from .index import router
from flask import request
from .. import db
from ..enums.role import Role
from ..middleware.auth_middleware import token_required
from ..models.DrivingTime import DrivingTime


def update_driving_time(hours_remaining, user_id):
    driving_time = DrivingTime.query.filter_by(user_id=user_id).first()

    if driving_time:
        driving_time.user_id = user_id
        driving_time.hours_total = hours_remaining + driving_time.hours_done
    else:
        driving_time = DrivingTime(hours_done=0, hours_total=hours_remaining, user_id=user_id)
    db.session.add(driving_time)
    db.session.commit()


def set_driving_time(hours_done, user_id):
    driving_time = DrivingTime.query.filter_by(user_id=user_id).first()

    if driving_time:
        driving_time.user_id = user_id
        driving_time.hours_done = driving_time.hours_done + hours_done
        db.session.add(driving_time)
    db.session.commit()


# UPDATE driving time
@router.route('/driving-time', methods=['PUT'])
@token_required
def update_driving_time_route(current_user):
    payload = request.get_json()
    hours = payload['hours']
    user_id = payload['user_id']

    # Authorize role
    if current_user.role == Role.Student:
        return 'Not allowed to add time', 401
    update_driving_time(hours, user_id)
    return 'driving hour created', 201
