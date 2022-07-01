from .index import router
from flask import request
from .. import db
from ..models.DrivingTime import DrivingTime


# Add time
@router.route('/time', methods=['POST'])
def add_time():
    payload = request.get_json()
    hours_done = payload['hours_done']
    user_id = payload['user_id']
    hours_total = payload['hours_total']
    driving_time = DrivingTime(hours_done=hours_done, hours_total=hours_total, user_id=user_id)
    db.session.add(driving_time)
    db.session.commit()
    return 'driving hour created', 201
