from flask import jsonify

from .User import User
from .. import db
from ..services.serializer import Serializer
from sqlalchemy.sql import func


class Meet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    start = db.Column(db.DateTime(timezone=True), default=func.now())
    end = db.Column(db.DateTime(timezone=True), default=func.now())
    all_day = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    chef = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.Column(db.Integer, db.ForeignKey('user.id'))

    def serialize_list(self):
        d = Serializer.serialize_list(self)
        return d

    def serialize(self):
        d = Serializer.serialize(self)
        d['user'] = User.serialize(User.query.filter_by(id=d['user']).first())
        d['chef'] = User.serialize(User.query.filter_by(id=d['chef']).first())
        return d
