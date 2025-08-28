from .. import db
from ..services.serializer import Serializer


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=False)

    def serialize_list(self):
        d = Serializer.serialize_list(self)
        return d

    def serialize(self):
        d = Serializer.serialize(self)
        return d
