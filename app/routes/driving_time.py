from .index import router
from flask import request
from .. import db
from ..enums.role import Role
from ..middleware.auth_middleware import token_required
from ..models.DrivingTime import DrivingTime


# UPDATE driving time
@router.route('/driving-time', methods=['PUT'])
@token_required
def update_driving_time(current_user):
    # Authorize role
    if current_user.role == Role.Student:
        return 'Not allowed to add time', 401
    payload = request.get_json()
    hours_done = payload['hours_done']
    user_id = payload['user_id']
    hours_total = payload['hours_total']

    # email already use
    driving_time = DrivingTime.query.filter_by(user_id=user_id).first()

    if driving_time:
        driving_time.user_id = user_id
        driving_time.hours_done = hours_done
        driving_time.hours_total = hours_total
    else:
        driving_time = DrivingTime(hours_done=hours_done, hours_total=hours_total, user_id=user_id)
    db.session.add(driving_time)
    db.session.commit()
    return 'driving hour created', 201
