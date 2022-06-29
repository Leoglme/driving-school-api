from .. import db
from ..services.serializer import Serializer
from sqlalchemy.sql import func


class Time(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    remaining = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)

    def serialize_list(self):
        d = Serializer.serialize_list(self)
        return d

    def serialize(self):
        d = Serializer.serialize(self)
        return d
