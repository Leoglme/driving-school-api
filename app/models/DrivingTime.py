from .. import db
from sqlalchemy.sql import func

class DrivingTime(db.Model):
    __tablename__ = 'driving_times'
    id = db.Column(db.Integer, primary_key=True)
    hours_done = db.Column(db.Integer, default=0)
    hours_total = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    @staticmethod
    def serialize_list(driving_times):
        return [dt.serialize() for dt in driving_times]

    def serialize(self):
        d = {
            'id': self.id,
            'hours_done': self.hours_done,
            'hours_total': self.hours_total,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id
        }
        if self.user:
            d['user'] = {
                'id': self.user.id,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name
            }
        return d