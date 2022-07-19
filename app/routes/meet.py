from sqlalchemy import desc
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
    title = payload['title']
    start = datetime.fromisoformat(payload['start'])
    end = datetime.fromisoformat(payload['end'])
    all_day = payload['allDay']
    chef = payload['chef']
    user = payload['user']
    meet = Meet(title=title, start=start, end=end, all_day=all_day, chef=chef, user=user)
    db.session.add(meet)
    db.session.commit()
    return 'Meet created', 201


# Get all meets
@router.route('/meets', methods=['GET'])
@token_required
def index_meet(current_user):
    meets = Meet.query.all()
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
    meet = Meet.query.filter_by(id=meet_id).first()
    if meet:
        db.session.delete(meet)
        db.session.commit()
        return 'Meet deleted'
    return f"Meet with id {meet_id} doesn't exist"
