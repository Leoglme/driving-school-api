from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from ..enums.role import Role
from ..services.serializer import Serializer


class User(db.Model):
    __tablename__ = 'users'
    Serialize_only = ('id', 'email', 'first_name', 'last_name')

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    role = db.Column(db.Integer)
    avatar = db.Column(db.String(255))
    passwordNeedSet = db.Column(db.Boolean, default=True)
    active = db.Column(db.Boolean, default=True)

    driving_time = db.relationship('DrivingTime', backref='user', uselist=False, lazy='select')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def serialize_list(users):
        return [u.serialize() for u in users]

    def serialize(self):
        d = Serializer.serialize(self)
        if self.driving_time:
            d['driving_time'] = self.driving_time.serialize()
        else:
            d['driving_time'] = {'hours_done': 0, 'hours_total': 0, 'hours_remaining': 0}

        d['driving_time']['hours_remaining'] = d['driving_time']['hours_total'] - d['driving_time']['hours_done']
        d['role'] = {
            'id': d['role'],
            'name': Role(d['role']).name
        }
        del d['password']
        return d