from .. import db
from ..services.serializer import Serializer


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))

    def serialize(self):
        d = Serializer.serialize(self)
        return d