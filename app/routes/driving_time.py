from .index import router
from flask import request
from .. import db
from ..middleware.auth_middleware import token_required
from ..models.DrivingTime import DrivingTime


# Add time
@router.route('/time', methods=['POST'])
@token_required
def add_time(current_user):
    payload = request.get_json()
    hours_done = payload['hours_done']
    user_id = payload['user_id']
    hours_total = payload['hours_total']
    driving_time = DrivingTime(hours_done=hours_done, hours_total=hours_total, user_id=user_id)
    db.session.add(driving_time)
    db.session.commit()
    return 'driving hour created', 201
