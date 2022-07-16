from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from ..enums.role import Role
from ..services.serializer import Serializer


class User(db.Model):
    Serialize_only = ('id', 'email', 'first_name', 'first_name')

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String())
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    role = db.Column(db.Integer)
    avatar = db.Column(db.String(255))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def serialize_list(self):
        d = Serializer.serialize_list(self)
        return d

    def serialize(self):
        d = Serializer.serialize(self)
        d['role'] = {
            'id': d['role'],
            'name': Role(d['role']).name
        }
        del d['password']
        return d
