from .index import router
from flask import request
from .. import db
from ..middleware.auth_middleware import token_required
from ..models.Meet import Meet
from flask import jsonify
from datetime import datetime


# Create meet
@router.route('/meet', methods=['POST'])
@token_required
def store_meet(current_user):
    payload = request.get_json()
    name = payload['name']
    date = datetime.fromisoformat(payload['date'])
    duration = payload['duration']
    student_id = payload['student_id']
    instructor_id = payload['instructor_id']
    meet = Meet(name=name, date=date, duration=duration, student_id=student_id, instructor_id=instructor_id)
    db.session.add(meet)
    db.session.commit()
    return 'Meet created', 201


# Get all meets
@router.route('/meets', methods=['GET'])
@token_required
def index_meet(current_user):
    meets = Meet.query.all()
    return jsonify(Meet.serialize_list(meets))


# Get meet by id
@router.route('/meet/<int:meet_id>', methods=['GET'])
@token_required
def show_meet(current_user, meet_id):
    meet = Meet.query.filter_by(id=meet_id).first()
    if meet:
        return jsonify(Meet.serialize(meet))
    return f"Meet with id {meet_id} doesn't exist"


# Update meet
@router.route('/meet/<int:meet_id>', methods=['PUT'])
@token_required
def update_meet(current_user, meet_id):
    meet = Meet.query.filter_by(id=meet_id).first()
    if meet:
        payload = request.get_json()
        meet.name = payload['name']
        meet.date = datetime.fromisoformat(payload['date'])
        meet.duration = payload['duration']
        meet.student_id = payload['student_id']
        meet.instructor_id = payload['instructor_id']
        db.session.commit()
        return 'Meet Updated'
    return f"Meet with id {meet_id} doesn't exist"


# Delete meet
@router.route('/meet/<int:meet_id>', methods=['DELETE'])
@token_required
def destroy_meet(current_user, meet_id):
    meet = Meet.query.filter_by(id=meet_id).first()
    if meet:
        db.session.delete(meet)
        db.session.commit()
        return 'Meet deleted'
    return f"Meet with id {meet_id} doesn't exist"
